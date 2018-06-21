import { FormBuilder, FormGroup, Validators, FormControl, AbstractControl } from '@angular/forms';
import { ReactiveFormsModule }                from '@angular/forms';

export const geneidValidator = (control: FormControl): {[key: string]: boolean} => {
  
  console.log(control.value);
  if (control.value != "" && control.value.includes('>')) {
    return { invalidIDS: true };
  }
  return null;
};