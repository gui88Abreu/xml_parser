#Desenvolvido por Guilherme Abreu com propósito didático para a disciplina EA876 ministrada na FEEC-UNICAMP

#importa a api necessaria para fazer busca de endereco usando o banco de dados dos correios
import pycep_correios

#faz a leitura do arquivo xml ignorando qualquer erro de decodificacao de caracteres
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

#casos de arquivos xml - os seguintes token sao utilizados como base para distinguir os diferentes arquivos xml
case1 = "NOTAS_FISCAIS"
case2 = "LoteNotaFiscal"
case3 = "CompNfse"
case4 = "ConsultarNfseFaixaResposta"
case5 = "ConsultarLoteRpsResposta"
case6 = "ConsultarNfseResposta"
case7 = "nfse"
case8 = "tcLotNFE"

#CASE 1 - arquivos simmples, onde eh preciso apenas identificar os campos corretos para encontrar o token correto
if case1 in token[3] or case8 in token[1]:
    for i in range(len(token)):
        if "PRESTADOR_CIDADE"  == token[i] or "tsMunPtd"  == token[i]:
            prestador = token[i+1]
        if "CIDADE_PRESTACAO" == token[i] or "tsMunSvc"  == token[i]:
            gerador = token[i+1]
        if "VALOR_SERVICO" == token[i] or "tsVlrSvc"  == token[i]:
            val_servico = token[i+1].replace(",", ".")
        if "VALOR_ISS" == token[i] or "tsVlrISSRet"  == token[i]:
            iss_retido = token[i+1].replace(",", ".")

#CASE 2 - arquivos mais complexos, exigindo a implementacao de uma pilha para encontrar corretamente o campo ncessario
if case2 in token[3] or case3 in token[3] or case4 in token[3] or case5 in token[3] or case6 in token[3] or case7 in token[1]:
    
    stack = []
    for i in range(len(token)):
        #Manipula um pilha para encontrar qual caso o programa esta tratando
        if "PrestadorServico" in token[i] or "prestador" in token[i]:
            if "PrestadorServico" in stack:
                stack.pop()
            else:
                stack.append("PrestadorServico")

        #Manipula um pilha para encontrar qual caso o programa esta tratando
        if "Servico" == token[i] or "ns3:Servico" == token[i] or "/Servico" == token[i] or "/ns3:Servico" == token[i]:
            if "Servico" in stack:
                stack.pop()
            else:
                stack.append("Servico")
        
        if "localPrestacao" in token[i]:
            if "localPrestacao" in stack:
                stack.pop()
            else:
                stack.append("localPrestacao")

        #Encontra o municipio atraves do cep, fazendo uso de uma conexao com o banco de dados dos correios
        if ("ns3:Cep" == token[i] or "Cep" == token[i] or "cep" == token[i]) and len(stack) > 0:
            if "PrestadorServico" == stack[0]:
                try:
                    endereco = pycep_correios.consultar_cep(token[i+1])
                    prestador = endereco['cidade']
                except:
                    continue
            else:
                try:
                    endereco = pycep_correios.consultar_cep(token[i+1])
                    gerador = endereco['cidade']
                except:
                    continue

        # Em alguns casos nao sera possivel encontrar o municipio atraves do cep, por isso sera necessario encontrar atraves do codigo do municipio
        if "CodigoMunicipio" in token[i] and len(stack) > 0 and (prestador == "None" or gerador == "None"):
            file = open("Cod_Mun.csv", "r", encoding="utf-8")
            lines = file.readlines()

            for line in lines:
                if token[i+1] in line:
                    line = line.split(",")
                    if stack[0] == "PrestadorServico" and prestador == "None":
                        prestador = line[0].replace('"', "")
                    if stack[0] == "Servico" and gerador == "None":
                        gerador = line[0].replace('"', "")
                    break
            file.close()
        
        #Identifica o municio gerador em um caso exclusivo
        if "descricaoMunicipio" == token[i] and len(stack) > 0:
            if stack[0] == "localPrestacao":
                gerador = token[i+1]

        #Identifica o valor dos servicos
        if "ns3:ValorServicos" == token[i] or "ValorServicos" == token[i] or "valorTotalServico" == token[i]:
            val_servico = token[i+1].replace(",", ".")
        
        #Identifica o valor do iss retido
        if "ns3:ValorIss" == token[i] or "ValorIss" == token[i] or "valorTotalISS" == token[i]:
            iss_retido = token[i+1].replace(",", ".")

if prestador == 'None' or gerador == 'None':
    print("ERROR: Um dos ceps informado não pôde ser encontrado com base nos dados dos correios,")
    print("Ou o codigo do municipio não pôde ser encontrado com base nos dados do ibge")

#Gera planilha .csv
print(gerador + ", " + prestador + ", " + val_servico + ", " + iss_retido)

