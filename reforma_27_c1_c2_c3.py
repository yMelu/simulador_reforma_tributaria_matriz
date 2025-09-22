class SimuladorReforma2027:
    def __init__(self, atividade, margem, custo,ano, 
                 aliq_iss=None, aliq_icms=None, cred_icms=None, 
                 aliq_cbs=0.0,
                 aliq_irpj=0.0, add_ir=0.0, aliq_csll=0.0,
                 pct_base_ir=0.0, pct_base_cs=0.0, pct_base_ircs= 0.0, despesas_cred= {}):

        self.ano = ano
        self.atividade = atividade
        self.margem = margem
        
        #ICMS
        self.aliq_iss = aliq_iss if atividade == 'Serviço' else 0
        self.aliq_icms = aliq_icms
        self.cred_icms = cred_icms
        
        #REFORMA
        self.aliq_cbs = aliq_cbs

        #IRCS
        self.aliq_irpj = aliq_irpj
        self.add_ir = add_ir
        self.aliq_csll = aliq_csll #p servico

        #Despesas livres de creditos
        self.despesas_cred = self.calc_creditos(despesas_cred)
        self.despesas_livres_creditos = sum(item['custo'] for item in self.despesas_cred.values())
        
        self.cmv = custo
        self.custo = custo + self.despesas_livres_creditos
        

        if atividade == 'Comércio':
            self.pct_base_ir = pct_base_ir
            self.pct_base_cs = pct_base_cs
            self.pct_base_ircs = pct_base_ircs
            self.irpj_efetivo = aliq_irpj * pct_base_ir
            self.csll_efetivo = aliq_csll * pct_base_cs
        else: 
            self.pct_base_ir = pct_base_ircs
            self.pct_base_cs = pct_base_ircs
            self.irpj_efetivo = aliq_irpj * pct_base_ircs
            self.csll_efetivo = aliq_csll * pct_base_ircs
        
        #PV
        self.preco_venda = self.descobrir_preco_venda()

    def descobrir_icms_ef(self, valor):
        icms_deb = valor * self.aliq_icms
        icms_cred = self.cmv * self.cred_icms
        icms_net = (icms_deb-icms_cred)/valor
        
        return icms_net
    
    def descobrir_despesa_ef(self,custo,dict_despesas):
        pass

    def calc_creditos(self,dict_despesas):
        for c in dict_despesas.keys():
            dict_despesas[c]['cred'] = round(dict_despesas[c]['base'] * self.aliq_cbs, 2)
            dict_despesas[c]['custo'] = round(dict_despesas[c]['bruto'] - dict_despesas[c]['cred'], 2)

        return dict_despesas
    
    def calcular_margem_real(self, preco_venda):
        icms = preco_venda * self.descobrir_icms_ef(preco_venda) 
        iss = preco_venda * self.aliq_iss
        add_ir = preco_venda * self.add_ir   # <<< adicional de IR como o PIS
        pv_antes_cbs = preco_venda - (icms + iss + add_ir) #PV -> preco_venda
        
        cbs = pv_antes_cbs * self.aliq_cbs
        
        #IRCS
        base_ir = preco_venda * self.pct_base_ir
        base_cs = preco_venda * self.pct_base_cs

        #Valores
        valor_ir = base_ir * self.aliq_irpj
        valor_cs = base_cs * self.aliq_csll


        lair = pv_antes_cbs - self.custo
        lucro_liquido = lair - (valor_ir + valor_cs)
    
        return {
            "margem": (lucro_liquido / preco_venda),
            "lucro_liquido": lucro_liquido,
            "receita_bruta": preco_venda,
            }
    
    def descobrir_preco_venda(self):
        #return 18825.3
        # Intervalo de busca binária
        baixo = self.custo
        alto = self.custo * 150000
        tolerancia = 0.0001
        max_iteracoes = 1_000_000

        for _ in range(max_iteracoes):
            meio = (baixo + alto) / 2
            margem_real = self.calcular_margem_real(meio)["margem"]

            if abs(margem_real - self.margem) < tolerancia:
                return meio
            elif margem_real < self.margem:
                baixo = meio
            else:
                alto = meio

        return (baixo + alto) / 2  # valor final aproximado
    
    def calcular_DRE(self):        
        icms = self.preco_venda * self.descobrir_icms_ef(self.preco_venda)
        add_ir = self.preco_venda * self.add_ir 
        iss = self.preco_venda * self.aliq_iss
        
        pv_antes_cbs = self.preco_venda - (icms + iss + add_ir) #PV -> preco_venda
        
        #IRCS
        base_ir = self.preco_venda * self.pct_base_ir
        base_cs = self.preco_venda * self.pct_base_cs

        #Valores
        valor_ir = base_ir * self.aliq_irpj
        valor_cs = base_cs * self.aliq_csll

        lair = pv_antes_cbs - self.custo
        #receita_liquida = preco_venda - (icms + cbs + valor_ir + valor_cs + iss)
        
        cbs = pv_antes_cbs * self.aliq_cbs

        lucro_liquido = lair - (valor_ir + valor_cs)
        margem = lucro_liquido / self.preco_venda
        
        dre = {
            "Custo Mercadoria/Servico": self.custo,
            "Margem de Lucro (%)": margem,
            "ICMS efetivo (%)":self.descobrir_icms_ef(self.preco_venda) ,
            #"aliq ISS (%)": self.aliq_iss,
            "aliq IR (%)":self.aliq_irpj ,
            "alic CSLL (%)":self.aliq_csll,
            "Base IR (%)":self.pct_base_ir,
            "base CS(%)":self.pct_base_cs,
            "CBS (%)":self.aliq_cbs,
            "Preço de venda":self.preco_venda,            
            "ICMS": icms,
            "Adicional IR (R$)": add_ir, 
            "Receita Base CBS": pv_antes_cbs,
            "Base IR":base_ir,
            "Base CS":base_cs,
            "Lucro antes IR/CS":lair,
            "IR Valor":valor_ir,
            "CS Valor":valor_cs,
            "Lucro Líquido":lucro_liquido,
            "Margem":margem,
            "Base CBS": pv_antes_cbs,
            "CBS VALOR":cbs,
            "Nota fiscal": self.preco_venda + cbs
        }

        return dre
    

