from flask import Flask, make_response, jsonify, request
from flask_pydantic_spec import FlaskPydanticSpec
from flask_pydantic_spec import Response, Request
from flask_cors import CORS
from pydantic import BaseModel
import json
import requests

app = Flask(__name__)
spec = FlaskPydanticSpec()
spec.register(app)
CORS(app)

class Documento(BaseModel):
    documento: str 

class Erro(BaseModel):
    status:int
    msg:str     

class Endereco(BaseModel):
    cep: str
    logradouro: str
    complemento: str
    bairro: str
    localidade: str
    uf: str
    
@app.post('/ValidarCPF')
@spec.validate(body=Request(Documento), resp=Response(HTTP_400=Erro,  HTTP_500=Erro), tags=['CPF'])
def Post():
    """
    Verifica se um cpf atende aos requisitos principais

    """
    body = request.context.body.dict()
    cpf = request.json
    
    #Retira apenas os dígitos do CPF, ignorando os caracteres especiais
    numeros = [int(digito) for digito in str(cpf['documento'])  if digito.isdigit()]
    
    #formatacao = False
    quant_digitos = False
    validacao1 = False
    validacao2 = False
    validacao3 = False
    
    #Verifica a estrutura do CPF (111.222.333-44)
    #if re.match(r'\d{3}\.\d{3}\.\d{3}-\d{2}', str(cpf['documento'])):
     #   formatacao = True

    if len(numeros) == 11:
        quant_digitos = True
    
        soma_produtos = sum(a*b for a, b in zip (numeros[0:9], range (10, 1, -1)))
        digito_esperado = (soma_produtos * 10 % 11) % 10
        if numeros[9] == digito_esperado:
            validacao1 = True

        soma_produtos1 = sum(a*b for a, b in zip(numeros [0:10], range (11, 1, -1)))
        digito_esperado1 = (soma_produtos1 *10 % 11) % 10
        if numeros[10] == digito_esperado1:
            validacao2 = True
        
        if  cpf['documento'] != "00000000000" and cpf['documento'] != "11111111111" and cpf['documento'] != "22222222222" and cpf['documento'] != "33333333333" and cpf['documento'] != "44444444444" and cpf['documento'] != "55555555555" and cpf['documento'] != "66666666666" and cpf['documento'] != "77777777777" and cpf['documento'] != "88888888888" and cpf['documento'] != "99999999999":
            validacao3 = True
            
        #and formatacao == True
        if quant_digitos == True  and validacao1 == True and validacao2 == True and validacao3 == True:
            return make_response(
            jsonify(Erro(status=200, msg="O CPF é válido").dict())), 200
        else:
            return make_response(
            jsonify(Erro(status=500, msg="O CPF não é válido.").dict())), 500

    else:
         return make_response(
            jsonify(Erro(status=500, msg="O CPF não é válido.").dict())), 500


@app.get('/ConsultarCEP/<cep>')
@spec.validate(resp=Response(HTTP_200=Endereco,HTTP_400=Erro,  HTTP_500=Erro), tags=['CEP'])
def Get(cep):
    """
    Verifica se um cep é válido e retorna as informações

    """   
    requestes = requests.get(f"https://viacep.com.br/ws/{cep}/json/")
      
    return make_response(
           jsonify(json.loads(requestes.text)))
    
app.run()         