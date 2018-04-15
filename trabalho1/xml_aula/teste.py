import pycep_correios

xml = ''
while 1:
    try:
        xml = xml + input()
    except EOFError:
        break
    except UnicodeDecodeError:
        continue

xml = xml.replace(">", "<") #troca as ocorrencias do primeiro caracter pelo segundo
token = xml.split("<") #retorna uma lista com os tokens separados pelo caracter especificado

#inicializa variaveis
prestador = 'None'
gerador = 'None'
val_servico = 'None'
iss_retido = 'None'

#casos de arquivos xml
case1 = "NOTAS_FISCAIS"
case2 = "LoteNotaFiscal"
case3 = "CompNfse"
case4 = "ConsultarNfseFaixaResposta"
case5 = "ConsultarLoteRpsResposta"
case6 = "ConsultarNfseResposta"

#CASE 1
if case1 in token[3]:
    for i in range(len(token)):
        if "PRESTADOR_CIDADE"  == token[i]:
            prestador = token[i+1]
        if "CIDADE_PRESTACAO" == token[i]:
            gerador = token[i+1]
        if "VALOR_SERVICO" == token[i]:
            val_servico = token[i+1].replace(",", ".")
        if "VALOR_ISS" == token[i]:
            iss_retido = token[i+1].replace(",", ".")

#CASE 2
if case2 in token[3] or case3 in token[3] or case4 in token[3] or case5 in token[3] or case6 in token[3]:
    
    stack = []
    for i in range(len(token)):
        if "PrestadorServico" in token[i]:
            if "PrestadorServico" in stack:
                stack.pop()
            else:
                stack.append("PrestadorServico")

        if "Tomador" in token[i]:
            if "Tomador" in stack:
                stack.pop()
            else:
                stack.append("Tomador")

        if "ns3:Cep" == token[i] or "Cep" == token[i]:
            if "PrestadorServico" == stack[0]:
                try:
                    if token[i+1] == "34000000":
                        prestador = "Nova Lima"
                    endereco = pycep_correios.consultar_cep(token[i+1])
                    prestador = endereco['cidade']
                except:
                    continue
            else:
                try:
                    if token[i+1] == "34000000":
                        gerador = "Nova Lima"
                    endereco = pycep_correios.consultar_cep(token[i+1])
                    gerador = endereco['cidade']
                except:
                    continue

        if "CodigoMunicipio" == token[i] and len(stack) > 0 and prestador == "None":
            file = open("Cod_Mun.csv", "r", encoding="utf-8")
            
            lines = file.readlines()

            for line in lines:
                if token[i+1] in line:
                    line = line.split(",")
                    if stack[0] == "PrestadorServico":
                        prestador = line[0].replace('"', "")
                    else:
                        gerador = line[0].replace('"', "")
                    break
            file.close()


        if "ns3:ValorServicos" == token[i] or "ValorServicos" == token[i]:
            val_servico = token[i+1].replace(",", ".")
        if "ns3:ValorIss" == token[i] or "ValorIss" == token[i]:
            iss_retido = token[i+1].replace(",", ".")


if prestador == 'None' or gerador == 'None':
    print("ERROR: Um dos ceps informado não pôde ser encontrado com base nos dados dos correios.")

print(gerador + ", " + prestador + ", " + val_servico + ", " + iss_retido)

