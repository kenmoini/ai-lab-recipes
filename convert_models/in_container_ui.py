import streamlit as st
import subprocess
import os
import boto3
from botocore.exceptions import ClientError

quantization_types = ["Q2_K","Q3_K_S","Q3_K_M", "Q3_K_L", "Q4_K_S",
                      "Q4_K_M", "Q5_K_S", "Q5_K_M", "Q6_K"]

st.title("🤗 GGUF Model Converter")

with st.sidebar:
    st.markdown("Tested Models:")
    st.code("TBD")
    
col1, col2 =st.columns(2)
with col1:
    s3_connection_type = st.selectbox(label="S3 Connection Type", 
                                options=["AWS S3", "Nooba"],index=1)
with col2:
    quantization = st.selectbox(label="Quantization Level", 
                                options=quantization_types,index=5) 

model_name = st.text_input(label="Enter a huggingface model url to convert",
                           placeholder="org/model_name")

keep_files = st.checkbox("Keep huggingface model files after conversion?")
submit_button = st.button(label="submit")

if submit_button:
    if f"{s3_connection_type}" == "AWS S3":
        access_key_id = os.environ.get('AWS_ACCESS_KEY_ID', "")
        secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY', "")
        bucket_name = os.environ.get('BUCKET_NAME', "")
        bucket_host = os.environ.get('BUCKET_HOST', "")
        bucket_port = os.environ.get('BUCKET_PORT', "443")
        bucket_protocol = os.environ.get('BUCKET_PROTOCOL', "https")
        bucket_region = os.environ.get('BUCKET_REGION', "")
        verifySSLEnv = os.environ.get("S3_VERIFY_SSL", "True")
    if f"{s3_connection_type}" == "Nooba":
        access_key_id = os.environ.get('AWS_ACCESS_KEY_ID', "")
        secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY', "")
        bucket_name = os.environ.get('BUCKET_NAME', "")
        bucket_host = os.environ.get('BUCKET_HOST', "s3.openshift-storage.svc")
        bucket_port = os.environ.get('BUCKET_PORT', "443")
        bucket_protocol = os.environ.get('BUCKET_PROTOCOL', "https")
        bucket_region = None
        verifySSLEnv = os.environ.get("S3_VERIFY_SSL", "False")
        
    bucket_endpoint = bucket_protocol + "://" + bucket_host + ":" + str(bucket_port)

    verifySSL = False
    if verifySSLEnv.lower() == "true":
        verifySSL = True

    s3_client = boto3.client('s3',
        endpoint_url=bucket_endpoint,
        aws_access_key_id=access_key_id,
        aws_secret_access_key=secret_access_key,
        region_name=bucket_region,
        verify=verifySSL)

    with st.spinner("Processing Model..."):
        process_env = os.environ.copy()
        process_env["HF_MODEL_URL"] = f"{model_name}"
        process_env["QUANTIZATION"] = f"{quantization}"
        process_env["KEEP_ORIGINAL_MODEL"] = f"{keep_files}"
        x = subprocess.Popen(["/opt/app-root/src/converter/run.sh", "converter"], env=process_env, stdout=subprocess.PIPE) 
        
        container_output = st.empty()
        response = []
        num_lines=0
        while x.poll() is None:
            line = x.stdout.readline().decode()
            num_lines += 1
            response.append(line)

            # Upload to S3
            modelName = f"{model_name}"
            quantType = f"{quantization}"
            splitModelPath = modelName.split("/")
            fileName = splitModelPath[0] + "-" + splitModelPath[1] + "-" + quantType + ".gguf"
            filePath = "/opt/app-root/src/converter/converted_models/gguf/" + fileName
            if os.path.isfile(filePath):
                s3_client.upload_file(filePath, bucket_name, fileName)

            if num_lines < 21:
                container_output.code("".join(response),
                                      language="Bash")
            else:
                container_output.code("".join(response[num_lines-21:num_lines]),
                                      language="Bash")
