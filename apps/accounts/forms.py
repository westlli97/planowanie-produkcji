from django import forms
from django.contrib.auth.models import Group

from apps.accounts.models import (
    AppPermission,
    JobFunction,
    OrganizationUnit,
    User,
    WorkerTypePermission,
)


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


class AppPermissionForm(forms.ModelForm):
    class Meta:
        model = AppPermission
        fields = ["code", "name", "description"]


class JobFunctionForm(forms.ModelForm):
    class Meta:
        model = JobFunction
        fields = ["name", "permissions", "is_administrator"]
        widgets = {"permissions": forms.CheckboxSelectMultiple}


class FunctionAssignmentForm(forms.Form):
    user = forms.ModelChoiceField(queryset=User.objects.filter(is_active=True), label="Użytkownik")
    job_function = forms.ModelChoiceField(queryset=JobFunction.objects.all(), label="Funkcja")


class PermissionOverrideForm(forms.Form):
    permission = forms.ModelChoiceField(queryset=AppPermission.objects.all(), label="Uprawnienie")
    user = forms.ModelChoiceField(
        queryset=User.objects.filter(is_active=True), label="Użytkownik", required=False
    )
    group = forms.ModelChoiceField(queryset=Group.objects.all(), label="Grupa", required=False)
    allowed = forms.BooleanField(required=False, label="Zezwól")

    def clean(self):
        cleaned_data = super().clean()
        if bool(cleaned_data.get("user")) == bool(cleaned_data.get("group")):
            raise forms.ValidationError("Wskaż dokładnie jednego użytkownika albo grupę.")
        return cleaned_data


class WorkerTypePermissionForm(forms.ModelForm):
    class Meta:
        model = WorkerTypePermission
        fields = ["worker_type", "permission"]
