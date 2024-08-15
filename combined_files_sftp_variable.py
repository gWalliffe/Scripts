import os
import zipfile
import pysftp

#codigo usado para extração e uniao de relatórios de wpp via marketingcloud

# Informações do servidor SFTP do Salesforce
sftp_host = @sftp_host
sftp_user = @sftp_user
sftp_pass = @sftp_pass
sftp_directory = @sftp_directory

# Diretório onde você deseja salvar os arquivos combinados
output_directory = @output_directory

# Lista dos estados (XXX) que você está interessado
IES = [@businessunit]  # Adicione mais estados se necessário

def download_and_extract_files(sftp, filename):
    local_filename = os.path.join(os.getcwd(), filename)

    sftp.get(os.path.join(sftp_directory, filename), local_filename)

    with zipfile.ZipFile(local_filename, 'r') as zip_ref:
        zip_ref.extractall()

    os.remove(local_filename)

def combine_files(sigla):
    combined_inbound = open(os.path.join(output_directory, f'combined_inbound.csv'), 'w', encoding='utf-8')
    combined_potencialunsubs = open(os.path.join(output_directory, f'combined_potencialunsubs.csv'), 'w', encoding='utf-8')
    combined_tracking = open(os.path.join(output_directory, f'combined_tracking.csv'), 'w', encoding='utf-8')

    for root, _, files in os.walk('.'):
        for filename in files:
            if filename.endswith('.csv') and sigla in filename:
                with open(os.path.join(root, filename), 'r', encoding='utf-8') as file:
                    content = file.read()
                    if 'inboundmessagelogs' in filename:
                        combined_inbound.write(content)
                    elif 'potencialunsubs' in filename:
                        combined_potencialunsubs.write(content)
                    elif 'tracking' in filename:
                        combined_tracking.write(content)

    combined_inbound.close()
    combined_potencialunsubs.close()
    combined_tracking.close()

def main():
    with pysftp.Connection(host=sftp_host, username=sftp_user, password=sftp_pass) as sftp:
        sftp.cwd(sftp_directory)

        for sigla in IES:
            filename = f'whatsapp_report_{sigla}.zip'
            download_and_extract_files(sftp, filename)
            combine_files(sigla)

            # Limpando os arquivos extraídos
            for root, _, files in os.getcwd():
                for file in files:
                    if file.endswith('.csv'):
                        os.remove(os.path.join(root, file))

if __name__ == "__main__":
    main()
