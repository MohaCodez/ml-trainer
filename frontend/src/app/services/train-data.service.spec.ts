import { TestBed } from '@angular/core/testing';

import { TrainDataService } from './train-data.service';

describe('TrainDataService', () => {
  let service: TrainDataService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(TrainDataService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
