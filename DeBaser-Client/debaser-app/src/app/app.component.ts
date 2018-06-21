import { Component, OnInit, NgZone, Inject }  from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ReactiveFormsModule }                from '@angular/forms';
import { NGValidators }                       from 'ng-validators';
import { MdDialog }                           from '@angular/material';
import { Modal }                              from 'angular2-modal/plugins/bootstrap';


import { Submit }                 from './submit.component';


@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
})

export class AppComponent {}