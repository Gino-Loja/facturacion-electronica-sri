# -*- coding: utf-8 -*-

import base64
from datetime import date
import os
import random
from typing import List, Tuple
from fastapi import APIRouter, Request
from app.models.digital_certicate import Digital_certificate
from app.models.invoice import Invoice, InfoToSignXml
from app.utils.create_access_key import createAccessKey
from app.utils.create_xml import createXml, jsonToXml
from app.utils.save_xml import save_xml_database
from app.utils.sign_xml import sign_xml_file
from app.utils.send_xml import send_xml_to_reception, send_xml_to_authorization
from app.utils.control_temp_file import createTempXmlFile, createTempFile
from app.utils.get_content_xml_file import get_content_xml_file
from dotenv import dotenv_values
from app.lib.conexion.pool import db_manager_instance

import xml.etree.ElementTree as ET

routerInvoice = APIRouter()
config = {
    **dotenv_values('.env')
}


@routerInvoice.post("/invoice/sign", tags=['Invoice'])
async def sign_invoice(request: Request, invoice: Invoice, usuario_id: int):
    try:
        # get connection
        connection = db_manager_instance.get_connection()
        cursor = connection.cursor()
        # create access key
        
        randomNumber = str(random.randint(1, 99999999)).zfill(8)
        accessKey = createAccessKey(
            documentInfo=invoice.documentInfo, randomNumber=randomNumber)

        # generate xml
        xmlData = createXml(info=invoice, accessKeyInvoice=accessKey)

        # xml name
        xmlFileName = str(accessKey) + '.xml'

        # xml string
        xmlString = xmlData['xmlString']

        # create temp files to create xml
        xmlNoSigned = createTempXmlFile(xmlString, xmlFileName)
        xmlSigned = createTempXmlFile(xmlString, xmlFileName)
        
        # print("1==",xmlNoSigned.name)
        # print("2==",xmlSigned.name)
        # get digital signature
        cursor.execute("SELECT certificado, password, fecha_caducidad FROM certificado_digital")
        result = cursor.fetchone()
        
        #  date of expiration
        fecha_caducidad = result[2]
        
        if fecha_caducidad < date.today():
            raise Exception("Firma electrónica caducada.")
        
        if not result:
            raise Exception("Firma electrónica no encontrada en la base de datos.")
        
        
        # digital_signature = base64.b64decode(result.certificado)
        certificado_decode_base64 = base64_decode(result[0])
        # Mapear la tupla a un modelo Digital_certificate
        # digital_certificate = Digital_certificate(
        #     certificado=certificado_base64,  # Primer campo de la tupla
        #     password=result[1],     # Segundo campo
        #     fecha_caducidad=fecha_caducidad  # Tercer campo
        # )
        
        
        certificateName = 'signature.p12'
        
        pathSignature = os.path.abspath('app/signature.p12')

        
        # print(f"Certificado: {certificado_base64}")
        # with open(pathSignature, 'rb') as file:
        #     digitalSignature = file.read()
        #     certificateToSign = createTempFile(digitalSignature, certificateName)
        path_to_certificate = createTempFile(certificado_decode_base64, certificateName)
            
        # password of signature
        passwordP12 = config['PASSWORD']
        infoToSignXml = InfoToSignXml(
            pathXmlToSign=xmlNoSigned.name,
            pathXmlSigned=xmlSigned.name,
            pathSignatureP12=path_to_certificate.name,
            passwordSignature=passwordP12)

        # sign xml and creating temp file
        isXmlCreated = sign_xml_file(infoToSignXml)

        # url for reception and authorization
        urlReception = config["URL_RECEPTION"]
        urlAuthorization = config["URL_AUTHORIZATION"]
        #path = 'C:/Users/ginol/AppData/Local/Temp/firma60.xml'
        # with open(path, 'r') as archivo:
        #     tree = ET.parse(archivo)
        #     root = tree.getroot()
        #print(ET.tostring(root, encoding='utf-8').decode('utf-8'))
        # send xml for reception
        isReceived = False
        if isXmlCreated:
            isReceived = await send_xml_to_reception(
                pathXmlSigned=xmlSigned.name,
                urlToReception=urlReception,
            )

        # send xml for authorization
        isAuthorized = False
        xmlSignedValue = None
        if isReceived:
            responseAuthorization = await send_xml_to_authorization(
                accessKey,
                urlAuthorization,
            )
            isAuthorized = responseAuthorization['isValid']
            # get xml signed content
            xmlSignedValue = responseAuthorization['xml']
            #print(f"Estado: {responseAuthorization}")
            #print(str(comprobante))
            # save xml signed in databaseW
            save_xml_database(xmlSigned.name,
                              responseAuthorization['status'],
                              accessKey,
                              usuario_id,
                              invoice
                             )
            os.unlink(xmlSigned.name)
            os.unlink(path_to_certificate.name)
            os.unlink(xmlNoSigned.name)
        return {
            'result': {
                'accessKey': accessKey,
                'isReceived': isReceived,
                'isAuthorized': isAuthorized,
                'xmlFileSigned': xmlSignedValue
            }
        }
    #FIXME: revisar al devolver none estoy retornando un valor que se acepta en la api aunque la llamada no se ha hecho correctamente
    except Exception as e:
        print(e)
        return {'result': None}



# @routerInvoice.get("/invoice/get", tags=['Invoice23'])
# async def get_invoice():
#     # Obtener conexión
#     connection = db_manager_instance.get_connection()
#     cursor = connection.cursor()

#     try:
#         # Ejecutar consulta
#         cursor.execute("SELECT certificado, password, fecha_caducidad FROM certificado_digital")
#         result:Tuple[Digital_certificate]     = cursor.fetchone()

#         if not result:
#             raise Exception("Firma electrónica no encontrada en la base de datos.")
        
#         # certificado_bytes = bytes(result[0])  # Convertir memoryview a bytes

#         # # Decodificar a Base64 si es necesario
#         # certificado_base64 = certificado_bytes.decode("utf-8")

#         certificado_base64 = base64_decode(result[0])
        
        
        


#         # Mapear la tupla a un modelo Digital_certificate
        
#         return {'result': 'ok'}
    
    
#     except Exception as e:
#         print(f"Error: {e}")
#         raise
#     finally:
#         # Liberar conexión
#         db_manager_instance.release_connection(connection)
  


    
def base64_decode(query: bytes) -> str:
    certificado_bytes = bytes(query)  # Convertir memoryview a bytes

        # Decodificar a Base64 si es necesario
    certificado_base64 = base64.b64decode(certificado_bytes)
    return certificado_base64
    
    