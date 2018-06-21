import { DebaserAppPage } from './app.po';

describe('debaser-app App', () => {
  let page: DebaserAppPage;

  beforeEach(() => {
    page = new DebaserAppPage();
  });

  it('should display message saying app works', () => {
    page.navigateTo();
    expect(page.getParagraphText()).toEqual('app works!');
  });
});
