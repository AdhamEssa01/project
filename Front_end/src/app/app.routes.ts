import { Routes } from '@angular/router';
import { LandingComponent } from './features/landing/landing.component';
import { AnalyzeComponent } from './features/analyze/analyze.component';
import { ResultsComponent } from './features/results/results.component';

export const routes: Routes = [
  { path: '', component: LandingComponent },
  { path: 'analyze', component: AnalyzeComponent },
  { path: 'results', component: ResultsComponent },
  { path: '**', redirectTo: '' },
];
