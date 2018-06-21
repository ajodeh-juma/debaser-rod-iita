import { NgModule }                                    from '@angular/core';
import { BrowserModule }                               from '@angular/platform-browser';
import { FormsModule, ReactiveFormsModule }            from '@angular/forms';
import { HttpModule }                                  from '@angular/http';
import { Observable }                                  from 'rxjs/Rx';
import { MatButtonModule, MatCheckboxModule }                              from '@angular/material';
import { MatCardModule } from '@angular/material/card';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatDialogModule } from '@angular/material/dialog';
//import { MatInputModule } from '@angular/material/input';
import { MatTooltipModule } from '@angular/material/tooltip';
import { CommonModule } from '@angular/common';
import { BrowserAnimationsModule}                     from '@angular/platform-browser/animations';
import { NgSpinKitModule } from 'ng-spin-kit';
import 'hammerjs';
import { ModalModule } from 'angular2-modal';
import { BootstrapModalModule } from 'angular2-modal/plugins/bootstrap';
//import { Md2Module }  from 'md2';
import {MATERIAL_COMPATIBILITY_MODE} from '@angular/material';
import {MatListModule} from '@angular/material/list';
import {MatSelectModule} from '@angular/material/select';
//import {MatFormFieldModule} from '@angular/material/form-field';
import {MatIconModule} from '@angular/material/icon';


import { AppComponent }           from './app.component';
import { HomeComponent }          from './home.component';
import { AboutComponent }         from './about.component';
import { TutorialComponent }      from './tutorial.component';
import { ContactComponent }       from './contact.component';
import { AppRoutingModule }       from './app-routing.module';

import { HomeResolve } from './home.resolve';
import { HomeService } from './home.service';

@NgModule({
  declarations: [
    AppComponent,
    HomeComponent,
    AboutComponent,
    TutorialComponent,
    ContactComponent,
  ],
  imports: [
    BrowserModule,
    FormsModule,
    HttpModule,
    //Md2Module,
    MatExpansionModule,
    //NoConflictStyleCompatibilityMode,
    ReactiveFormsModule,
    AppRoutingModule,
    BrowserAnimationsModule,
    //MatDialog,
    MatButtonModule,
    MatCheckboxModule,
    MatCardModule,
    NgSpinKitModule,
    BootstrapModalModule,
    MatDialogModule,
    MatTooltipModule,
    MatListModule,
    MatSelectModule,
    MatIconModule,
    //MatInputModule,
    //MatFormFieldModule,
    //MatDialogRef, 
    
    //NoopAnimationsModule,
    ModalModule.forRoot(),

  ],
  //xports: [BrowserModule, BrowserAnimationsModule],
  providers: [
    HomeResolve, 
    HomeService,
    {provide: MATERIAL_COMPATIBILITY_MODE, useValue: true},
    
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }


/*
Copyright 2017 Google Inc. All Rights Reserved.
Use of this source code is governed by an MIT-style license that
can be found in the LICENSE file at http://angular.io/license
*/
