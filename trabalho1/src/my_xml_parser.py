#Desenvolvido por Guilherme Abreu com propósito didático para a disciplina EA876 ministrada na FEEC-UNICAMP

#funcao procura pelo endereco atraves do cep
def catch_city(cep):
    municipio = 'None'
    try:
        endereco = pycep_correios.consultar_cep(cep)
        municipio = endereco['cidade']
    except:
        pass
    return municipio

try:
    #importa a api necessaria para fazer busca de endereco usando o banco de dados dos correios
    import pycep_correios
except:
    pass

#faz a leitura do arquivo xml ignorando qualquer erro de decodificacao de caracteres
xml = ''
while 1:
    try:
        xml = xml + input()
    except EOFError:
        break
    except UnicodeDecodeError:
        continue

#segmenta o arquivo lido em tokens e armazena em uma lista chamada token
xml = xml.replace(">", "<")
token = xml.split("<")

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

#CASE 1 - arquivos simples, onde eh preciso apenas identificar os campos corretos com comparacoes
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
        
        #Manipula pilha para distinguir os campos cep e codigo do municipio para a hierarquia do prestador
        if "PrestadorServico" in token[i] or "prestador" in token[i]:
            if "prestador" in stack:
                stack.pop()
            else:
                stack.append("prestador")

        #Manipula pilha para distinguir os campos cep e codigo do municipio para a hierarquia do gerador
        if "OrgaoGerador" in token[i] or "localPrestacao" in token[i]:
            if "gerador" in stack:
                stack.pop()
            else:
                stack.append("gerador")

        #Encontra o municipio atraves do cep, fazendo uso de uma conexao com o banco de dados dos correios
        if ("ns3:Cep" == token[i] or "Cep" == token[i] or "cep" == token[i]) and len(stack) > 0:
            if "prestador" == stack[0]:
                prestador = catch_city(token[i+1])
            else:
                gerador = catch_city(token[i+1])
                
        #Em alguns casos nao sera possivel encontrar o municipio atraves do cep, por isso sera necessario encontrar atraves do codigo do municipio
        if "CodigoMunicipio" in token[i] and len(stack) > 0 and (prestador == "None" or gerador == "None"):
            file = open("Cod_Mun.csv", "r", encoding="utf-8")
            lines = file.readlines()

            for line in lines:
                if token[i+1] in line:
                    line = line.split(",")
                    if stack[0] == "prestador" and prestador == "None":
                        prestador = line[0].replace('"', "")
                    if stack[0] == "gerador" and gerador == "None":
                        gerador = line[0].replace('"', "")
                    break
            file.close()
        
        #Identifica o municio gerador em um caso exclusivo onde o campo que possui o municipio gerador possui a tag <descricaoMunicipio>
        if "descricaoMunicipio" == token[i] and len(stack) > 0:
            if stack[0] == "gerador":
                gerador = token[i+1]

        #Identifica o valor do servico
        if "ns3:ValorServicos" == token[i] or "ValorServicos" == token[i] or "valorTotalServico" == token[i]:
            val_servico = token[i+1].replace(",", ".")
        
        #Identifica o valor do iss retido
        if "ns3:ValorIss" == token[i] or "ValorIss" == token[i] or "valorTotalISS" == token[i]:
            iss_retido = token[i+1].replace(",", ".")

#Informa o usuario caso o programa nao tenha coseguido encontrar algum daod
if prestador == 'None' or gerador == 'None' or val_servico == 'None' or iss_retido == 'None':
    print("ERROR: O programa não foi capaz de encontrar um ou mais dados com as informações fornecidas no arquivo XML")

#Gera planilha .csv
print(gerador + ", " + prestador + ", " + val_servico + ", " + iss_retido)