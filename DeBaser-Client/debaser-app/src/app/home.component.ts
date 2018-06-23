import { Component, OnInit, NgZone, Inject, Pipe, PipeTransform, ChangeDetectionStrategy, ViewEncapsulation }           from '@angular/core';
import { FormBuilder, FormGroup, Validators, FormControl, AbstractControl, FormArray }               from '@angular/forms';
import { ReactiveFormsModule }                                                                       from '@angular/forms';
import { NGValidators }                                                                              from 'ng-validators';
import { MatButtonModule, MatCheckboxModule, MatCardModule, MatDialog, MatDialogRef }                              from '@angular/material';
import { Observable } from 'rxjs/Rx';
import { Router, ActivatedRoute } from '@angular/router';
import { NgSpinKitModule } from 'ng-spin-kit'
import { Submit }                                                                                    from './submit.component';
import { HomeService }                                                                               from './home.service';
import { geneidValidator }                                                                           from './geneid-validator';
import { fastaseqValidator }                                                                         from './fastaseq-validator';
import { varietiesValidator }                                                                        from './varieties-validator';
import { outputformatValidator }                                                                     from './output-format-validator';
import { selectedVariatiesValidator }                                                                from './selected-varieties-validator';
import { DialogRef, ModalComponent } from 'angular2-modal';
import { BSModalContext, BootstrapModalModule, Modal } from 'angular2-modal/plugins/bootstrap';
import { ModalModule } from 'angular2-modal';




@Component({
  changeDetection: ChangeDetectionStrategy.OnPush,
  selector: 'my-home',
  templateUrl: './home.component.html',
  styleUrls: ['./app.component.css'],
  providers: [ HomeService ],
  encapsulation: ViewEncapsulation.None
})



export class HomeComponent implements OnInit {
  //get version(): string {
  //  return window.angular2ModalVer;
  //}
  isMenuExpanded = false;
  species_db: any=[];                         // populate species/references/organisms from the backend/server
  varieties_db: any=[];                       // populate varieties from the backend/server
  multiplegeneid_db: any=[];
  outputformats_db: any=[];
  resultsgeneids_db: any=[];
  DefaultOutArray = ['consensus'];           // Default array for output options - consensus FASTA file
  outputArray = [];
  selectedVarieties = [];                    // an array to store the selected varieties ids from the varieties database
  loading = false;  
  checkFor:string;



  unselectedAll: any[];
  selectedAll: any[];

  selectedFormats = [];
  arrayCheck = ['Consensus (FASTA format)'];
  outArray = ['Muscle', 'Multalin'];
  outputfmtArray = [];

  consensusOUT = [];
  alignmentOUT = ['Consensus'];

  outputBoxArray: FormArray;  

  inputTYPE: string;
  intype: string;
  organism: string;
  varieties: any[];
  geneid: string;
  sequence: string;
  outputfmt: string;
  uuid: string;
  uid: string;
  resultLink:any;
  cookieValue: string;
  selectedOrg:string;
  selectedVars = [];
  datas = [];

  allvarieties:any[];

  results;
  control1: FormArray;
  
  form: FormGroup;
  seqform: FormGroup;
  gidform: FormGroup;
  fastaform: FormGroup;


  
  selectedOrganism: string;
  currentVariety = [];
  selectedVariety = [];
  errorMessage: string;

  disabled = true;
  

  
     


  submission = {};

  singleOptions = [
    { text: 'consensus',  checked: true,  },
  ];

  multipleOptions = [
    
    { text: 'muscle',     checked: false, },
    { text: 'multalin',   checked: false, },
  ];

  INPUT_TYPE = {
    SEQID: 'Gene identifier',
    SEQ:  'FASTA sequence',
    SUBMITDATA: 'Click here for raw data assembly',
  };


constructor( private homeService: HomeService, private fb: FormBuilder, private formBuilder: FormBuilder, private route: ActivatedRoute, private router: Router, private modal: Modal) {

    
    this.gidform = this.formBuilder.group({
      'organism':  [null, Validators.required],
      //'varieties': ['', Validators.required],
      'outputfmt': ['', Validators.required],

    });

    this.fastaform = this.formBuilder.group({
      'sequence':  ['', [Validators.required, fastaseqValidator]],
    });
    
    
    this.form = this.formBuilder.group({
      'inputTYPE': ['', Validators.required],
      //'organism':  [null, Validators.required],
      //'varieties': ['', Validators.required],
      'geneid':    ['', [Validators.required, geneidValidator]],
      //'outputfmt': [null, Validators.required],
  });

  this.seqform = this.formBuilder.group({
      //'inputTYPE': ['', Validators.required],
      //'organism':  [null, Validators.required],
      //'varieties': ['', Validators.required],
      'sequence':  ['', [Validators.required, fastaseqValidator]],
      //'outputfmt': ['', [Validators.required, outputformatValidator]],
  });



}


ngOnInit() {

    console.log(this.fetchSpecies());
    console.log(this.fetchVarieties());
    this.results = this.route.snapshot.data['results'];
    console.log(this.results);
    console.log(this.fetchGeneidResults());
    console.log(this.fetchMultiplegeneidResults());
    console.log(this.selectedVariety);
    console.log(this.selectedOrg);
    this.selectedFormats.push(this.singleOptions[0].text);
    this.setAnalysisInputType(this.INPUT_TYPE.SEQID);

}



aboutmodal() {
  this.modal.alert()
    .size('lg')
    .showClose(true)
    .title('About DeBaser')
    .body(`
        <p>
            <b>DeBaser</b>, is a multi-functional tool principally designed to locate polymorphisms between the coding sequences of multiple varieties of a single plant species. In addition to serving as indicators of the cause of phenotypic difference, knowledge of polymorphisms are important when designing RNAi tools such as artificial miRNA or VIGS constructs. In addition to providing the sequence information for any selected variety, the multi-sequence alignment tools, MultiAlin and Muscle, are built in for immediate polymorphism detection. DeBaser utilises transcriptomic data generated through NGS. This is stored as assembled transcriptomes available for immediate use on-line.  Unprocessed data can be assembled upon request and will be added to the website generally within 72 hours. 
        </p>
        <p>
            <b>DeBaser online polymorphism finder</b>, contains the transcriptomic data for a large number of varieties for multiple plant species (currently IITA’s mandate crops). Select a species/organism and one or more varieties to retrieve the transcriptome data for inputted gene identifiers or FASTA format sequences.  MultiAlin and/or Muscle can be selected to provide multi-sequence alignments. See the tutorial for instructions.
            
        </p>
        <p>
            <b>DeBaser NGS assembly pipeline</b>, can be used if a desired variety is not already included on the online platform. DeBaser includes a bioinformatic pipeline comprising <a href="https://genomebiology.biomedcentral.com/articles/10.1186/gb-2009-10-3-r25">Bowtie</a>, <a href="https://www.ncbi.nlm.nih.gov/pubmed/19505943">Samtools</a> and <a href="http://www.popgen.dk/angsd/index.php/ANGSD">ANGSD</a> and can be utilised upon request. The pipeline does not perform de novo assembly or provide read counts. Rather, it rapidly produces a consensus sequence through read assembly against a reference genome. The assembly is then included on the online platform for comparison against the existing varieties. Click the ‘Submit raw data for assembly’ to access the submission page
            <br>
            
             
        </p>

        <div class="infosectioncontent">
              <dl>
              <dt>Reference genomes:  The following are currently used as reference genomes for NGS raw data assembly. User can use alternate reference genomes upon request.</dt>
                  <dd>
                  <ul>
                    <li>
                      Cassava:  Manihot esculenta v6.1 Accession ID: LTYI01000000 <a href="https://phytozome.jgi.doe.gov/pz/portal.html#!info?alias=Org_Mesculenta">[Phytozome]</a>
                    </li>
                    <li>
                      Banana:  Musa acuminata v1  <a href="https://phytozome.jgi.doe.gov/pz/portal.html#!info?alias=Org_Macuminata">[Phytozome]</a>
                    </li>
                    <li>
                      Cowpea:  Vigna unguiculata v1.1 <a href="https://phytozome.jgi.doe.gov/pz/portal.html#!info?alias=Org_Vunguiculata_er">[Phytozome]</a>
                    </li>
                    <li>
                      Yam:  Vigna unguiculata v1.1 <a href="https://phytozome.jgi.doe.gov/pz/portal.html">[Phytozome]</a>
                    </li>

                  </ul>
                      
                  </dd>
              <dt>Varieties</dt>
                  <dd>
                      Raw sequencing data and all alignment information from high throuput sequencing platforms are obtained from the <a href="https://www.ncbi.nlm.nih.gov/sra">NCBI SRA portal</a>.
                  </dd>
              </dl>
        </div>
      `)
    .open();
}

tutorialmodal(){
  this.modal.alert()
  .size('lg')
  .showClose(true)
  .title('Tutorial')
  .body(`
  <div class="panel panel-default margin-15">
    
  </div>
    <ol class="list-group">
      <p>
        <b>A. DeBaser online polymorphism finder</b>
      </p>
      <li class="list-group-item">
        Step 1. Choose organism.
      </li>
      <li class="list-group-item">
        Step 2. Choose one or more varieties. Selecting two or more varieties will enable the multi-alignment options.
      <br>
      </li>
      <li class="list-group-item">
        Step 3. Select the input type and Paste one or more sequences (FASTA format) or gene identifiers appropriately.
      </li>
      <li class="list-group-item">
        Step 4. If required, select the desired multiple sequence alignment options (Multalin and/or Muscle).Click the submit button
      </li>
      <li class="list-group-item">
        Step 5. The results, both the sequence information for each variety chosen and, if selected, multi-sequence alignments will appear automatically.
      </li>

    </ol>
    <ol class="list-group">
      <p>
        <b>B. DeBaser NGS assembly pipeline</b>
      </p>
      <li class="list-group-item">
        The assembly pipeline is not available online. Click ‘‘Submit raw data for assembly’ to open the data submission page
      </li>
    </ol>
  `)
  .open();
}

contactmodal() {
  this.modal.alert()
  .size('lg')
  .showClose(true)
  .title('Contact us')
  .body(`
    <div class="panel panel-default margin-15">
    
    </div>
        
      
      <ol class="list-group">
        <p>
          <b>Guidelines on submission of data and other enquiries</b>
        </p>
        <li class="list-group-item">
          Persons: Rodney Eyles, Trushar shah.
        </li>
        <li class="list-group-item">
          Email: debaser@iita.org.
        </li>
      </ol>
    
  `)
  .open();
}

usage1modal() {
  this.modal.alert()
  .size('lg')
  .showClose(true)
  .title('Submitting gene identifiers as input type')
  .body(`
    <li class="list-group-item">
      Paste sequence identifier(s) similar to the selected organism's genome (assembly version).</b><b> Below are examples of gene identifiers for Cassava v6.1 genome assembly</b><br>

    <br>
    
  
                    <pre>
Manes.03G052800.1
Manes.09G063700.1
Manes.03G098700.4
                    </pre>
    <b> Enter valid identifiers !</b>
    <br>
    </li>
  `)
  .open();
}




usage2modal() {
  this.modal.alert()
  .size('lg')
  .showClose(true)
  .title('Submitting FASTA sequences as input type')
  .body(`
    <li class="list-group-item">
      Paste FASTA sequence (s).</b><b> Below are examples of FASTA sequences for Cassava v6.1 genome assembly</b><br>

    <br>
    
  
                    <pre>
>seq1
ATCTGATGGACTGGATYATAAACTC
ACCATGATAGGGTTACCGATAGCAT
>seq2
AGCTGCTAGACTGGATYATAAAGCA
ACCATGATAGGGTTACCGATGAGGA
>seq3
ACCGATCCTAGGGATTCAAACTAGA
GCAATGACCCATGCATGATAGCAGTA
                    </pre>
    <b> Enter valid FASTA Sequence !</b>
    <br>
    </li>
  `)
  .open();
}

submitmodal() {
  this.modal.alert()
  .size('sm')
  .showClose(true)
  .title('Running job' +' '+ this.uid)
  .body(`
    <div class="col-xs-8">
      <div *ngIf="loading">
        <sk-fading-circle class="loader"></sk-fading-circle>
        <small style="margin-left: 40%">Thank you for submitting data, Please Wait</small>
      </div>
    </div>
  `)
  .open();
}

setAnalysisInputType (inputTYPE: string) {

   // update input type value

  const ctrl = this.form.get('inputTYPE');
  ctrl.setValue(inputTYPE);
  console.log(inputTYPE);
  
}

uniqID () {
	var number = Math.random()
	number.toString(36);
	this.uid = number.toString(36).substr(2, 9);
	console.log(this.uid);
}

setCookie(name=this.uid, exdays=2) {
	var d = new Date();
	d.setTime(d.getTime() + (exdays * 24 * 60 * 60 * 1000));
	var expires = "expires="+ d.toUTCString();
	document.cookie = name + '=' + this.uid +"; " + expires;
	console.log(document.cookie);
}

getCookie(name) {
	name = name + "=";
	var cookies = document.cookie.split(';');
	for (let i = 0; i < cookies.length; i++) {
		var cookie = cookies[i];
		while (cookie.charAt(0) == ' ') {
			cookie = cookie.substring(1);
		}
		if (cookie.indexOf(name) == 0) {
			return cookie.substring(name.length, cookie.length);
		}
	}
	return "";
}


UpdateOutFmt(value, event) {
	if (this.selectedVars.length === 1) {
		this.selectedFormats = ['consensus'];
	}
	else {
		if (event.target.checked) {
			this.selectedFormats.push(value);
		}
		else if (!event.target.checked) {
			const index = this.selectedFormats.indexOf(value);
			this.selectedFormats.splice(index, 1);
		}
	}
	console.log(this.selectedFormats);
}



//isChecked(id) {
//	var match = false;
//	this.matching = match;
//	for (let i = 0; i < this.data.length; i++) {
//		
//		if (this.data[i].id === id) {
//			var match = true;
//			this.matching = match;
//		}
//	}
//	return this.matching;	
//}

//sync(bool, item) {
//	if (bool) {
//		this.data.push(item);
//	} else {
//		for (let i = 0; i < this.data.length; i++) {
//			
//			if (this.data[i].id == item.id) {
//				this.data.splice(i, 1);
//			}
//		}
//	}
//}

//checkCookie() {
//	var jobid=this.getCookie(this.uid);
//	if (jobid != "") {
//		alert("Results for jobid" + jobid);
//	} else {
//		jobid = prompt("Please input the jobid:", "");
//		if (jobid != "" && jobid != null) {
//			this.setCookie(this.uid, jobid, 30);
//		}
//	}
//}

//deleteCookie(name) {
//	this.setCookie(name, "", -1);
//}

//loadingSpinner(){
//  this.loading = false;
//}



submitGeneID(value) {
	this.loading = true;

	// 1. generate a unique value with time as the seed value

	this.uid = Math.random().toString(36).substr(2, 9);
	console.log(this.uid);

	// 2. set that value as a cookie on the browser

	var d = new Date();
	d.setTime(d.getTime() + (2 * 24 * 60 * 60 * 1000));
	var expires = "expires="+ d.toUTCString();
	document.cookie = name + '=' + this.uid +"; " + expires;
	console.log(document.cookie);

	// get cookies

	var cookies = document.cookie.split(';');
	for (let cookie of document.cookie.split('; ')) {
		let [name, value] = cookie.split("=");
		cookies[name] = decodeURIComponent(value)

	}
	this.cookieValue = cookies[value];
	console.log(this.cookieValue);
  
  console.log(this.selectedFormats);
  //console.log(this.gidform.get('varieties').value);


 // 3. Add that value to submissions

	this.homeService.submitGeneIdData({
		inputTYPE: this.form.get('inputTYPE').value,
    //organism: this.selectedOrg,
		organism: this.gidform.get('organism').value,
		varieties: this.selectedVars,
		geneid: this.form.get('geneid').value,
		outputfmt: this.selectedFormats.toString(),
		//outputfmt: this.outputfmtArray.toString(),
		uuid: this.uid,
	}).subscribe(data => { 
	  console.log(data.varieties.length);
	  if (data.varieties.length == 1) {
	    this.checkFor="http://localhost/media/results-geneids/"+this.uid+"_consensuslink.html";
	  }
	  else {
	    this.checkFor="http://localhost/media/multi-results-ids/"+this.uid+"_links.html";
	  }
      console.log(this.checkFor);
      window.location.href=this.checkFor;
      this.loading = false;
      this.form.reset()
      console.log(data, 'on submitting');
	  }
	);
  
	//alert("Thank you for submitting data, Please Wait");
  //  window.location.reload(this.checkFor);
  
}




submitSeq(value) {

  this.loading = true;

  // 1. generate a unique value with time as the seed value

  this.uid = Math.random().toString(36).substr(2, 9);
  console.log(this.uid);

  // 2. set that value as a cookie on the browser

  var d = new Date();
  d.setTime(d.getTime() + (2 * 24 * 60 * 60 * 1000));
  var expires = "expires="+ d.toUTCString();
  document.cookie = name + '=' + this.uid +"; " + expires;
  console.log(document.cookie);

  // get cookies

  var cookies = document.cookie.split(';');
  for (let cookie of document.cookie.split('; ')) {
    let [name, value] = cookie.split("=");
    cookies[name] = decodeURIComponent(value)

  }
  this.cookieValue = cookies[value];
  console.log(this.cookieValue);


 // 3. Add that value to submissions
  this.homeService.submitSequenceData({
    organism: this.selectedOrg,
    //organism: this.seqform.get('organism').value,
    varieties: this.selectedVars,
    sequence: this.seqform.get('sequence').value,
    //outputfmt: this.outputfmtArray.toString(),
    outputfmt: this.selectedFormats.toString(),
    uuid: this.uid,
  }).subscribe(data => {
     console.log(data.varieties.length);
	  if (data.varieties.length == 1) {
	    this.checkFor="http://localhost/media/results-geneids/"+this.uid+"_consensuslink.html";
	  }
	  else {
	    this.checkFor="http://localhost/media/multi-results-ids/"+this.uid+"_links.html";
	  }

      console.log(this.checkFor);
      window.location.href=this.checkFor;
      this.loading = false;
      console.log(data, 'on submitting');
    }
  );
  //alert("Thank you for submitting data, Please Wait");
  //  window.location.reload();
}

fetchSpecies() {
  this.homeService.fetchSpecies()
    .subscribe(
      species => this.species_db = species,
      error => this.errorMessage = error,
    () => console.log(this.species_db));
}


fetchVarieties() {
  this.homeService.fetchVarieties()
    .subscribe(
      varieties => this.varieties_db = varieties,
      error => this.errorMessage = error,
      () => console.log(this.varieties_db));
  }


//fetchOutputFormats() {
//  this.homeService.fetchOutputFormats()
//    .subscribe(
//        outputformats => this.outputformats_db = outputformats,
//        error => this.errorMessage = error,
//        () => console.log(this.outputformats_db));
//}

fetchGeneidResults() {
  this.homeService.fetchGeneidResults()
    .subscribe(
      resultsgeneids => {
        this.resultsgeneids_db = resultsgeneids
        
        }
      )

      error => {this.errorMessage = error} 
}

fetchMultiplegeneidResults() {
  this.homeService.fetchMultiplegeneidResults()
    .subscribe(
      //() => this.loading = false,
      resultsmultiplegeneids => {
        this.multiplegeneid_db = resultsmultiplegeneids
        console.log(this.multiplegeneid_db);
        }
      )

      error => {this.errorMessage = error} 
}



onSelect_db(id): number {
  this.currentVariety = [];
  this.selectedVarieties = [];
  this.selectedVars = [];
  // load the species and connect to varieties for each
  for (let i = 0; i < this.species_db['results'].length; i++) {
    if (this.species_db['results'][i]['id'] === +id) {
      this.selectedOrg = this.species_db['results'][i]['id'];
      this.varieties_db = this.species_db['results'][i]['varieties'];
      
      //console.log('Varieties for organism ' + this.species_db['results'][i]['species_name'] + ' of id no: ' + this.species_db['results'][i]['id'] + ' are: ');
      for (let j = 0; j < this.varieties_db.length; j++){
          console.log(this.varieties_db[j]['variety_name'] + ' of id no: ' + this.varieties_db[j]['id']);
          //console.log(this.varieties_db[j]['species']['id']);

          }
        }
      }
      return 0;
  }

selectAll() {
	for (let i = 0; i < this.varieties_db.length; i++) {
		this.varieties_db[i].selected = this.selectedAll;
		
	}
}

checkIfAllSelected() {
	this.selectedAll = this.varieties_db.filter(function(data:any) { return data.selected == true });
	this.unselectedAll = this.varieties_db.filter(function(data:any) { return data.selected == false });
	console.log(this.selectedAll.length);
	console.log(this.unselectedAll);
	for (let i = 0; i < this.selectedAll.length; i++) {
		if(this.selectedVars.includes(this.selectedAll[i].id)) {
			
		}

	}
	this.selectedVars = [];
	for (let i = 0; i < this.selectedAll.length; i++) {
		this.selectedVars.push(this.selectedAll[i].id);
		this.selectedVars = Array.from(new Set(this.selectedVars));
	}
	console.log(this.selectedVars);
}

toggleSelect(event) {
  this.allvarieties = event.target.checked;
  this.varieties_db.forEach(function(item){
  console.log(item);
  item.selected = event.target.checked;
  
  
  });

}



ApplyFilters(isValid: boolean, id, event) {

  
  this.datas  = this.varieties_db.filter(function (data) { return data.selected == true });
  console.log(this.datas.length); 

  for (let i = 0; i < this.datas.length; i++) {
  	const ind = this.datas.indexOf(id);
    if(!this.selectedVars.includes(this.datas[i].id)){
      this.datas.splice(ind, 1);
      console.log(this.datas);
    }
  }
  
  if (!isValid) 
  	
  return;         
}


getVariety_db(val) {
  return Array.from(val);
  }

getSelectedVariety(id, event) {
  
  console.log('The selected target\'s id is:' + id);
  if (event.target.checked) {
    this.selectedVarieties.push(id);
    this.selectedVars.push(id);
    
    
  } else {
    if (!event.target.checked) {
      const indexx = this.selectedVarieties.indexOf(id);
      const indexxx = this.selectedVariety.indexOf(id);
      const ind = this.selectedVars.indexOf(id);

      this.selectedVarieties.splice(indexx, 1);
      this.selectedVars.splice(ind, 1);
      }
    
    }
    
    console.log('The currently selected targets are: ' + this.selectedVars);
    
  }


updateCheck(value, event) {
	//this.consensusOUT = [];
	console.log(this.selectedVarieties.length);
	if (this.selectedVarieties.length === 1) {
		this.consensusOUT = [];
		if (event.target.checked) {
      this.consensusOUT.push(value);
    }
    else if (!event.target.checked) {
      const indexx = this.consensusOUT.indexOf(value);
      this.consensusOUT.splice(indexx, 1);
    }
    
    this.outputfmtArray = Array.from(new Set(this.consensusOUT))
    console.log(this.outputfmtArray);
    }

	
	 
	else {
	  if (event.target.checked) {
        this.alignmentOUT.push(value);
      }
      else if (!event.target.checked) {
        const indexx = this.alignmentOUT.indexOf(value);
        this.alignmentOUT.splice(indexx, 1);
      }

      this.outputfmtArray = Array.from(new Set(this.alignmentOUT))
      console.log(this.outputfmtArray);
	}
  } 

  //seqout_options () {
  //  for (let i = 0; i < this.output_options.length; i++) {
  //    var option = this.output_options[i];
  //    this.submission[option.id] = option.default;
  //    console.log(this.submission);
  //    
  //  }
  //}



}