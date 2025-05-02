from django import forms


class KatilimForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        label='Adınız',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'İsim Soyisim'})
    )
    student_id = forms.CharField(
        max_length=10,
        label='Öğrenci Numaranız',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Öğrenci Numarası'})
    )
    department = forms.ChoiceField(
        choices=(
            (1, "Bilişim Sistemleri Ve Teknolojileri"),
            (2, "Bankacılık Ve Sigortacılık"),
            (3, "Halkla İlişkiler Ve Reklamcılık"),
            (4, "Gümrük İşletme"),
            (5, "Uluslararası Ticaret Ve Finansman"),
            (6, "Diğer"),
        ),
        label='Bölümünüz',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
