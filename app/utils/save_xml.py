from datetime import datetime
import logging
from lxml import etree
from app.lib.conexion.pool import db_manager_instance
import json
from pydantic import BaseModel

from app.models.invoice import Invoice

def save_xml_database(comprobante: str,
                      estado: str, 
                      numero_autorizacion: str, 
                      usuario_id: int,
                      json_info: Invoice):  # Type hint for clarity
    try:
        # Leer el archivo XML firmado como texto
        with open(comprobante, 'r', encoding='utf-8') as f:
            xml_signed = f.read()

        # Obtener la fecha y hora actual
        connection = db_manager_instance.get_connection()
        cursor = connection.cursor()

        fecha_autorizacion = datetime.now()

        # Crear el nodo raíz <autorizacion>
        autorizacion_xml = etree.Element('autorizacion')
        etree.SubElement(autorizacion_xml, 'estado').text = estado
        etree.SubElement(autorizacion_xml, 'numeroAutorizacion').text = numero_autorizacion
        etree.SubElement(autorizacion_xml, 'fechaAutorizacion').text = fecha_autorizacion.strftime("%d/%m/%Y %H:%M:%S")

        # Agregar el comprobante dentro de una sección CDATA
        comprobante_element = etree.SubElement(autorizacion_xml, 'comprobante')
        comprobante_element.text = etree.CDATA(xml_signed)

        # Crear el árbol XML
        xml_string = etree.tostring(autorizacion_xml, pretty_print=True, encoding='utf-8').decode('utf-8')

        # Convert Invoice object to JSON string
        json_string = None
        if isinstance(json_info, BaseModel):
            # If it's a Pydantic model
            json_string = json_info.model_dump_json()
        else:
            # Fallback to dict conversion if it's not a Pydantic model
            json_string = json.dumps(json_info.__dict__)
        
        try:
            insert_query = """
            INSERT INTO facturas_detalles (usuario_id, fecha_emision, estado, clave_acceso, xml_firmado, numero_factura, factura_json)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            
            cursor.execute(insert_query, (
                usuario_id,
                fecha_autorizacion,
                estado,
                numero_autorizacion,
                xml_string,
                numero_autorizacion,
                json_string  # Now we're passing a JSON string
            ))
            
            connection.commit()
            
        except Exception as e:
            print(f"Error en la base de datos: {e}")
            connection.rollback()
            raise
        finally:
            cursor.close()
            db_manager_instance.release_connection(connection)
       
        logging.info('Guardado el XML firmado en la base de datos')

    except Exception as e:
        print(f"Error al guardar el XML: {e}")
        raise