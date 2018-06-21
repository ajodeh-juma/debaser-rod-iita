import { FormBuilder, FormGroup, Validators, FormControl, AbstractControl } from '@angular/forms';
import { ReactiveFormsModule }                from '@angular/forms';

export const varietiesValidator = (control: AbstractControl): {[key: string]: boolean} => {
  
  console.log(control.value.length);
  if (!control.value || control.value != true || control.value.length === 0) {
    return { invalidVar: true };
  }
  return null;
};