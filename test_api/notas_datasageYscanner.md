
datasage 
caso 1: consulta especifica ej: cuanto facturo galana el mes pasada? (galana es un cliente)
pasos 
1 - api registros/metadata
    procesos disponibles y me quedo con el que me sirve 
2 - decision: reporte o panel de registro, que necesito para esta decision?
        neceisto los procesos disponibles + los que sean reportes -> de los que son reportes la informacion del reporte (campos de proceso -> describe los filtros del reporte) 
        si no existe un reporte que me sirva -> panel de registro (del excel la hoja columnas de paneles de registro)
        output seria : el reporte a utilizar o la informacion para el panel de registro
    2.1 - api formularios del reporte - llamo al Operator (que sabe como llenar formularios de reportes) ouput -> reporte en pdf (filtro de salida)
    2.2 - api reporte/panel de API registro/data 
        contexto de los datos para API: donde ? -> API registro/data 
            input   codigo del cliente (dado)
                    los demas campos los adquiere del contexto(excel)
                    pegada la api 
            output  los datos (json) datos raw
            post procc datos -> respuesta datos de la suma  


scanner 
caso 1: como cargo una nota de credito al sistema
    Alcance identifica enel menu el formulario que me permite conmpletar la solicitud y busca dentro de los BPM si ese formulario esta asociado a un proceso par apdoer explicar los siguientes pasos a realizar. NO accede a datos de negocios, solo metadata
    pasos: 
        api menu par asaber que procesos de menu (no tiene porque ser proceso BPM) tiene este usuario.
        que procesos BMP hay 
        proceso menu y proceso BPM estan linkeados o no? 
            si estan linkeados -> proceso menu es el proceso BPM y traigo detalles del flujo
            si no estan linkeados -> lleno el formulario 
        output: proceso menu y detalles del flujo BPM asociado a ese formulario

Operator 
caso 1: como cargo una nota de credito al sistema?
    proceso menu existe un formulario a llenar?
    llenar formulario con data de prompt