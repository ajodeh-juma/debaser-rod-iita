import { NgModule }             from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

import { AppComponent }         from './app.component';
import { HomeComponent }        from './home.component';
//import { AboutComponent }       from './about.component';
//import { TutorialComponent }    from './tutorial.component';
import { ContactComponent }     from './contact.component';
import { HomeResolve } from './home.resolve';


const routes: Routes = [
  { path: '', redirectTo: '/home', pathMatch: 'full' },
  { path: 'home', component: HomeComponent, resolve: {results: HomeResolve}},
  //{ path: 'about', component: AboutComponent },
  //{ path: 'tutorial', component: TutorialComponent },
  { path: 'submit-raw-data', component: ContactComponent }
];


@NgModule({
  imports: [ RouterModule.forRoot(routes) ],
  exports: [ RouterModule ]
  
})  

export class AppRoutingModule {}