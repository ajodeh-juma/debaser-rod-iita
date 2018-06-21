import { Injectable } from '@angular/core';
import { Router, Resolve, RouterStateSnapshot, ActivatedRouteSnapshot } from '@angular/router';
import { HomeService } from './home.service';
import { Observable }                                from 'rxjs/Rx';
@Injectable()

export class HomeResolve implements Resolve<any> {
	constructor(private homeService: HomeService) {}

	resolve(route: ActivatedRouteSnapshot):Observable<any> {
		let id = +route.params['id']
		return this.homeService.fetchGeneidResults();
	}
}