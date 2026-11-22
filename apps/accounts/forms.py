from django import forms

from apps.accounts.models import OrganizationUnit, User


class OrganizationUnitForm(forms.ModelForm):
    class Meta:
        model = OrganizationUnit
        fields = ["name", "parent", "is_active"]
        widgets = {"name": forms.TextInput(attrs={"class": "form-input"})}

    def clean_parent(self):
        parent = self.cleaned_data.get("parent")
        if parent and self.instance.pk:
            ancestor = parent
            while ancestor is not None:
                if ancestor.pk == self.instance.pk:
                    raise forms.ValidationError("Nie można przenieść jednostki pod jej potomka.")
                ancestor = ancestor.parent
        return parent


class MembershipForm(forms.Form):
    user = forms.ModelChoiceField(
        queryset=User.objects.filter(is_active=True).order_by("username"), label="Użytkownik"
    )
    organization_unit = forms.ModelChoiceField(
        queryset=OrganizationUnit.objects.filter(is_active=True), label="Jednostka"
    )
    is_primary = forms.BooleanField(required=False, label="Główna przynależność")
