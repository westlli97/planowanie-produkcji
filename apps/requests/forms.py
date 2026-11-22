from django import forms
from django.forms import BaseInlineFormSet, inlineformset_factory

from apps.requests.models import ProductionRequest, RequestItem


class ProductionRequestForm(forms.ModelForm):
    class Meta:
        model = ProductionRequest
        fields = ["request_type", "priority", "due_date", "erp_reference_number"]
        widgets = {
            "request_type": forms.Select(attrs={"x-model": "requestType"}),
            "due_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = (
                field.widget.attrs.get("class", "")
                + " min-h-11 w-full rounded-lg border border-slate-300 px-3"
            ).strip()


class RequestItemForm(forms.ModelForm):
    class Meta:
        model = RequestItem
        fields = ["erp_index", "quantity", "unit", "comment"]
        widgets = {
            "quantity": forms.NumberInput(attrs={"step": "0.001", "inputmode": "decimal"}),
            "comment": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["quantity"].required = False
        self.fields["unit"].required = False
        for field in self.fields.values():
            field.widget.attrs["class"] = (
                field.widget.attrs.get("class", "")
                + " min-h-11 w-full rounded-lg border border-slate-300 px-3"
            ).strip()


class BaseRequestItemFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        if any(self.errors):
            return

        filled_items = []
        for form in self.forms:
            if not hasattr(form, "cleaned_data") or form.cleaned_data.get("DELETE", False):
                continue
            data = form.cleaned_data
            if any(data.get(field) for field in ("erp_index", "quantity", "unit", "comment")):
                filled_items.append(data)

        if not filled_items:
            raise forms.ValidationError("Dodaj co najmniej jedną pozycję.")

        if self.instance.request_type == ProductionRequest.RequestType.INDEX_ORDER:
            if any(not item.get("erp_index", "").strip() for item in filled_items):
                raise forms.ValidationError(
                    "Każda pozycja zamówienia indeksów musi zawierać indeks ERP."
                )


RequestItemFormSet = inlineformset_factory(
    ProductionRequest,
    RequestItem,
    form=RequestItemForm,
    formset=BaseRequestItemFormSet,
    extra=1,
    can_delete=False,
)
