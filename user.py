class Usuario(): #Creamos la clase Humano
    def __init__(self, nombre, apellido, nit, saldo_actual): 
        self.nombre = nombre 
        self.apellido = apellido 
        self.nit = nit
        self.saldo_actual = saldo_actual
        
        
    def presentar(self):
        presentacion = ("Hola soy {} {}, mi cedula es:  {} mi saldo es: {}") 
        print(presentacion.format(self.nombre, self.apellido, self.nit, self.saldo_actual))

    def get_saldo_actual(self):
        return self.saldo_actual

    def __str__(self):
        cadena=self.nombre+","+self.apellido+","+self.nit.__str__()+","+self.saldo_actual.__str__()
        return cadena        
        
