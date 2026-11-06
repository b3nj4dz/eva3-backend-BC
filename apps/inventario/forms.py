from django import forms
from .models import EquipoInformatico


class EquipoInformaticoForm(forms.ModelForm):
    class Meta:
        model = EquipoInformatico
        fields = [
            'codigo_sku', 
            'nombre', 
            'categoria', 
            'especificaciones', 
            'tarifa_diaria',
            'precio_venta',
            'monto_garantia', 
            'stock', 
            'estado', 
            'imagen', 
            'destacado', 
            'activo'
        ]
        widgets = {
            'codigo_sku': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. LAP-I7-16GB'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Laptop Asus TUF i7'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'especificaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Detalla CPU, GPU, RAM, SSD...'}),
            'tarifa_diaria': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'precio_venta': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'monto_garantia': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'destacado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_tarifa_diaria(self):
        tarifa = self.cleaned_data.get('tarifa_diaria')
        if tarifa is not None and tarifa < 0:
            raise forms.ValidationError("La tarifa diaria no puede ser negativa.")
        return tarifa

    def clean_precio_venta(self):
        precio = self.cleaned_data.get('precio_venta')
        if precio is not None and precio < 0:
            raise forms.ValidationError("El precio de venta no puede ser negativo.")
        return precio

    def clean_monto_garantia(self):
        garantia = self.cleaned_data.get('monto_garantia')
        if garantia is not None and garantia < 0:
            raise forms.ValidationError("El monto de garantía no puede ser negativo.")
        return garantia