from django import forms

from apps.accounts.models import OrganizationUnit, User
from apps.production.models import ProductionTask


class ProductionTaskForm(forms.ModelForm):
    class Meta:
        model = ProductionTask
        fields = [
            "title",
            "description",
            "assigned_unit",
            "assigned_user",
            "priority",
            "due_date",
            "production_request",
        ]
        widgets = {"due_date": forms.DateInput(attrs={"type": "date"})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["assigned_unit"].queryset = OrganizationUnit.objects.filter(is_active=True)
        self.fields["assigned_user"].queryset = User.objects.filter(is_active=True).order_by(
            "username"
        )
        self.fields["assigned_unit"].required = False
        self.fields["assigned_user"].required = False
        self.fields["due_date"].required = False
        self.fields["production_request"].required = False
        for field in self.fields.values():
            field.widget.attrs["class"] = (
                field.widget.attrs.get("class", "")
                + " min-h-11 w-full rounded-lg border border-slate-300 px-3"
            ).strip()

    def clean(self):
        cleaned_data = super().clean()
        assigned_unit = cleaned_data.get("assigned_unit")
        assigned_user = cleaned_data.get("assigned_user")
        if bool(assigned_unit) == bool(assigned_user):
            raise forms.ValidationError("Wybierz dokładnie jedną jednostkę albo jedną osobę.")
        return cleaned_data


class TaskTransferForm(forms.Form):
    assigned_user = forms.ModelChoiceField(
        queryset=User.objects.filter(is_active=True).order_by("username"),
        label="Przypisz do pracownika",
    )
