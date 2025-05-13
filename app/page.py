import requests
import streamlit as st
import time 
import boto3
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

s3_client =  boto3.client('s3')
bucket_name = st.secrets["BUCKET_S3"]
endpoint = st.secrets["API_ENDPOINT"]

def genereate_filename(profile_name, file_format):
    """Generate a filename based on the profile name and file format."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    extension = "csv" if file_format.lower() == "csv" else "json"
    return f"{profile_name.replace('/', '_')}_{timestamp}.{extension}"

def check_s3_for_file(bucket_name, filename, max_wait_time=900, check_interval=5):
    """Polls S3 for a file matching the prefix and returns its key."""
    if not s3_client:
        st.error("Cliente S3 não inicializado. Não é possível verificar o bucket.")
        return None

    start_time = time.time()
    st.info(f"Gerando arquivo '{filename}' ...")
    # Placeholders for dynamic updates in Streamlit UI
    progress_bar = st.progress(0)
    status_text = st.empty()

    while time.time() - start_time < max_wait_time:
        elapsed_time = time.time() - start_time
        progress = int((elapsed_time / max_wait_time) * 100)
        progress_bar.progress(min(progress, 100)) 

        try:
            # List objects in S3 bucket with the specified prefix
            response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=filename)

            # Check if any objects were found
            if 'Contents' in response and len(response['Contents']) > 0:
                for obj in response['Contents']:
                    if obj['Key'] == filename:
                        status_text.success(f"Arquivo gerado: {filename}")
                        progress_bar.progress(100) 
                        return True 
                
        except Exception as e:
            st.error(f"Erro inesperado ao verificar S3: {e}")
            progress_bar.empty()
            status_text.empty()
            return None # Stop polling on unexpected error

        # Wait before the next S3 check
        time.sleep(check_interval)

    # If loop finishes without finding the file
    status_text.warning(f"Tempo limite ({max_wait_time}s) excedido. Arquivo com prefixo '{filename}' não encontrado.")
    print(f"Polling S3 timed out para prefixo {filename} no bucket {bucket_name}")
    progress_bar.empty() 
    return None

def genereate_download_link(bucket_name, filename, expiration=86400):
    """Generates a presigned URL for downloading an S3 object."""
    if not s3_client:
        st.error("Cliente S3 não inicializado. Não é possível gerar link.")
        return None
    
    try:
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': filename},
            ExpiresIn=expiration 
        )
        return url
    
    except Exception as e:
        st.error(f"Erro ao gerar link de download: {e}")
        print(f"Erro inesperado ao gerar presigned URL: {e}", exc_info=True)
        return None
    
st.markdown("""
<style>
    .reportview-container {
        background: linear-gradient(to right, #f64f59, #c471ed, #12c2e9);
    }
    .main {
        background-color: rgba(255,255,255,0.8);
        padding: 20px;
        border-radius: 10px;
    }
    .stButton>button {
        color: white;
        background-color: #4CAF50;
        border: none;
        border-radius: 4px;
        padding: 10px 24px;
        font-size: 16px;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
</style>
""", unsafe_allow_html=True)

# Interface Streamlit
st.title('📷 Reels Scrapper')

col1, col2 = st.columns(2, gap="large")

def call_extractor_api(profile: str, file_format: str, number_of_reels: int, filename: str):
    try:
        response = requests.get(
            endpoint,
            params={"profile": profile, "file_format": file_format, "number_of_reels": number_of_reels, "filename": filename},
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API request failed: {response.status_code}")
            return None 

    except Exception as e:
        st.error(f"Error calling API: {str(e)}")
        return None

with col1:
    st.subheader("Entrada de Dados")

    instagram_profile = st.text_input(
        'Digite um perfil do Instagram ou URL', 
        placeholder='@exemplo ou https://www.instagram.com/exemplo'
    )

    max_number_reels = 10
    number_of_reels = st.selectbox('Selecione o número de reels que serão extraídos', list(range(1, max_number_reels + 1)))
    
    # Botão para gerar link
    if st.button('🚀 Processar dados'):
        if instagram_profile:
            with st.spinner('Processando... Isso pode levar alguns minutos.'):
                filename = genereate_filename(instagram_profile, "csv")
                result = call_extractor_api(instagram_profile, "csv", number_of_reels, filename)
                if result:
                    transcription_file = f"transcription_{filename}"
                    # Check if the file is available in S3
                    file_found = check_s3_for_file(bucket_name, transcription_file)
                    if file_found:
                        download_url = genereate_download_link(bucket_name, transcription_file)
                        if download_url:
                            st.success('Link de download gerado com sucesso!')
                            st.markdown(f"**Clique para baixar:** [Link para download]({download_url})")
                else:
                    st.error('Falha ao gerar o link. Tente novamente mais tarde.')
        else:
            st.error('Por favor, forneça um perfil do Instagram ou uma URL.')
with col2:
    st.subheader("Instruções")
    st.info("""
    1. Digite o perfil do Instagram ou a URL.  
    2. Selecione o tipo de arquivo de retorno.  
    3. Clique em 'Processar dados' para obter um link do arquivo. 
    4. O link gerado tem duração de 24 horas. 
    """)

# Adicionar um footer
st.markdown("---")
st.markdown("Desenvolvido por Permatech")