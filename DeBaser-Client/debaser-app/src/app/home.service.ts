import { Injectable }                                from '@angular/core';
import { Headers, Http, Response, RequestOptions}    from '@angular/http';
import { MdDialogRef, MdDialog }                     from '@angular/material';
import { Observable }                                from 'rxjs/Rx';
import 'rxjs/add/operator/map';
import 'rxjs/add/observable/throw';
import 'rxjs/add/operator/toPromise';


import { Submit }                           from './submit.component';
import { SubmitSeq }                        from './submit-seq.component';


@Injectable()
export class HomeService {
  private headers = new Headers({'Content-Type': 'application/json; charset=UTF-8'});
  private options = new RequestOptions({ headers: this.headers });
  private varietiesUrl = 'http://localhost/varieties/';
  private speciesUrl = 'http://localhost/species/';
  private outputformatUrl = 'http://localhost/out-formats/';
  private submitgeneidUrl = 'http://localhost/geneids/';
  private submitsequenceUrl = 'http://localhost/sequences/';
  private resultgeneidsUrl = 'http://localhost/results-geneids/'
  private multiplegeneidsUrl = 'http://localhost/multi-results-ids/'

  loading: boolean = false;
  //uid: string;


  constructor(
    private http: Http) {
  }

  //loadingSpinner(){
  //  this.loading = false;
  //}
  
  submitGeneIdData(submit:Submit):Observable<Submit> {
    const body = JSON.stringify(submit);
    
    return this.http
      .post(this.submitgeneidUrl, body, this.options)
      .map(this.extractData)
      .catch(this.handleErrorObservable);


  }


  submitSequenceData(submitseq:SubmitSeq):Observable<Submit> {
    const body = JSON.stringify(submitseq);
    return this.http
      .post(this.submitsequenceUrl, body, this.options)
      .map(this.extractData)
      .catch(this.handleErrorObservable);
  }


  private extractData(res: Response) {
    let body = res.json();
    return body || { };
  }
  private handleError(error: Response | any) {
    let errMsg: string;
    if (error instanceof Response) {
      const body = error.json() || '';
      const err = body.error || JSON.stringify(body);
      errMsg = `${error.status} - ${error.statusText || ''} ${err}`;
    } else {
      errMsg = error.message ? error.message : error.toString();
    }
    console.error(errMsg);
    return Observable.throw(errMsg);

  }
  handleErrorObservable(error: Response | any) {
    console.error(error.message || error);
    return Observable.throw(error.message || error);
  }

  fetchSpecies(): Observable<any[]> {
    return this.http
    .get(this.speciesUrl, this.options)
    .map(this.extractData)
    .catch(this.handleError);
  }

  fetchVarieties(): Observable<any[]> {
    return this.http
      .get(this.varietiesUrl, this.options)
      .map(this.extractData)
      .catch(this.handleError);
  }

  fetchOutputFormats(): Observable<any> {
    return this.http
    .get(this.outputformatUrl, this.options)
    .map(this.extractData)
    .catch(this.handleError);
  }

  fetchGeneidResults(): Observable<any> {
    return this.http
    .get(this.resultgeneidsUrl, this.options)
    .map(this.extractData)
    .catch(this.handleError);
  }

  fetchMultiplegeneidResults(): Observable<any> {
    return this.http
    .get(this.multiplegeneidsUrl, this.options)
    .map(this.extractData)
    .catch(this.handleError);
  }
}