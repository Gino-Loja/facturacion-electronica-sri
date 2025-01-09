# -*- coding: utf-8 -*-
import os
import subprocess
import logging
import chardet

from app.utils.create_xml import saveXml

import chardet
import logging

def convert_to_utf8(input_path):
    try:
        # Leer el archivo en formato binario
        with open(input_path, 'rb') as file:
            raw_data = file.read()

        # Detectar la codificación del archivo
        result = chardet.detect(raw_data)
        encoding = result['encoding']
        # Leer el contenido con la codificación detectada
        with open(input_path, 'r', encoding=encoding) as file:
            content = file.read()

        # Convertir el contenido a UTF-8
        content_utf8 = content.encode('utf-8').decode('utf-8')

        # Guardar el contenido convertido en UTF-8 en el archivo de salida
        with open(input_path, 'w', encoding='utf-8') as file:
            file.write(content_utf8)

    except Exception as e:
        print(f"Error al convertir el archivo a UTF-8: {e}")

class Xades(object):
    def sign(self, xml_no_signed_path, xml_signed_path, file_pk12_path, password):
        JAR_PATH = 'FirmaElectronica/FirmaElectronica.jar'
        JAVA_CMD = 'java'
        path_jar_to_sign = os.path.join(os.path.dirname(__file__), JAR_PATH)
        
        try:
            command = [
                JAVA_CMD,
                '-jar',
                path_jar_to_sign,
                xml_no_signed_path,
                file_pk12_path,
                password,
                xml_signed_path
            ]
            subprocess.check_output(command)
        except subprocess.CalledProcessError as e:
            returnCode = e.returncode
            output = e.output
            logging.error('Llamada a proceso JAVA códig: %s' % returnCode)
            logging.error('Error: %s' % output)

        # Ejecutar el comando de firma
        p = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )

        res = p.communicate()

        # Convertir el archivo firmado temporal a UTF-8
        try:
            
            convert_to_utf8(xml_signed_path)
        except Exception as e:
            print(f"Error al convertir y guardar el archivo firmado: {e}")

        return res[0]
