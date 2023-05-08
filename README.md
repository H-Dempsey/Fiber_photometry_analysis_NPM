# Fiber_photometry_analysis_NPM
GUI for the analysis of data from the NPM (Neurophotometrics) Fiber Photometry System. <br>

![image](https://user-images.githubusercontent.com/101311642/236769619-c9528927-04ff-44fe-af31-e18d1acc5258.png)

### Simple installation

Download the executable file for Mac or PC and double click to open it (note that it will take a while to start up). <br>

### Anaconda installation

Install [Anaconda Navigator](https://www.anaconda.com/products/distribution). <br>
Open Anaconda Prompt (on Mac open terminal and install X-Code when prompted). <br>
Download this repository to your home directory by typing in the line below.
```
git clone https://github.com/Andrews-Lab/Fiber_photometry_analysis_NPM.git
```
If you receive an error about git, install git using the line below, type "Y" when prompted and then re-run the line above.
```
conda install -c anaconda git
```
Change the directory to the place where the downloaded folder is. <br>
```
cd Fiber_photometry_analysis_NPM
```

Create a conda environment and install the dependencies.
```
conda env create -n NPM -f Dependencies.yaml
```

To use these codes, close and re-open Anaconda Prompt (or Terminal on Mac) <br>
Change the directory to the place where the git clone was made.
```
cd Fiber_photometry_analysis_NPM
```

Activate the conda environment.
```
conda activate NPM
```

Run the codes.
```
python Codes/Run_program.py
```

### Guide
All the text in the GUI windows have explanations, which you can access by hovering your cursor over the text. <br>
This should be comprehensive enough to provide all the instructions for a guide.
<p align="center">
<img src="https://user-images.githubusercontent.com/101311642/236766390-d2f16647-e198-44b2-812f-bb24a6e91ac8.png" width="400">

## Here is the manual scoring workflow
<p align="center">
<img src="https://user-images.githubusercontent.com/101311642/233562882-cbdd7ed9-9006-4f71-9831-ab451b96f2bc.png" width="400">
<img src="https://user-images.githubusercontent.com/101311642/233562658-ab237e67-a909-4c99-a91e-b32b80695586.png" width="400">
<img src="https://user-images.githubusercontent.com/101311642/233562695-bd67b693-5835-47fc-be44-b3627381118e.png" width="400">
<img src="https://user-images.githubusercontent.com/101311642/233562705-b1406064-fea6-4886-9604-ab26bce7c30a.png" width="400">

## Here is the multi-folder group analysis workflow
<p align="center">
<img src="https://user-images.githubusercontent.com/101311642/233562917-df8bfcaa-7394-483c-9522-fa5a374863a7.png" width="400">
<img src="https://user-images.githubusercontent.com/101311642/233562930-3b5c5596-56ce-4573-b9fe-973134fbb7ff.png" width="400">
<img src="https://user-images.githubusercontent.com/101311642/233562947-6e7047a8-6834-49b4-b991-80aa8c81b453.png" width="400">
<img src="https://user-images.githubusercontent.com/101311642/233564053-aaaec711-00a9-4b9c-bf0d-3a5b521d5a16.png" width="400">
<img src="https://user-images.githubusercontent.com/101311642/233564085-cf4aefc1-0301-4c80-9aa8-4d9aa6793a99.png" width="400">

## Here is the single folder peri-events analysis workflow
<p align="center">
<img src="https://user-images.githubusercontent.com/101311642/233563085-0b4418f3-cc49-4a79-b098-ae4a1982efe0.png" width="400">
<img src="https://user-images.githubusercontent.com/101311642/233563126-d040e81d-337a-45d8-8948-48782bc31dbc.png" width="400">
<img src="https://user-images.githubusercontent.com/101311642/233563141-1649e298-a0ee-49d5-9d3b-a6b87c66bd20.png" width="400">
<img src="https://user-images.githubusercontent.com/101311642/233563149-a299d8a5-1d4e-41f6-b108-5b858d96f9f3.png" width="400">
<img src="https://user-images.githubusercontent.com/101311642/233563170-dfb94914-898a-43df-a45a-434577ce1b17.png" width="400">
<img src="https://user-images.githubusercontent.com/101311642/233563242-b15ee588-025c-469a-bcf9-bda6b5004a62.png" width="400">

## Here is the single folder whole recording analysis workflow
<p align="center">
<img src="https://user-images.githubusercontent.com/101311642/233563085-0b4418f3-cc49-4a79-b098-ae4a1982efe0.png" width="400">
<img src="https://user-images.githubusercontent.com/101311642/233563487-c6ce6657-3cd6-4376-ade6-edfca11b12fd.png" width="400">
<img src="https://user-images.githubusercontent.com/101311642/233563598-3be691d6-a533-4c64-b548-e8c93a978cbd.png" width="400">
<img src="https://user-images.githubusercontent.com/101311642/233563933-e98105b3-0368-43ca-8089-8261a58124c0.png" width="400">
<img src="https://user-images.githubusercontent.com/101311642/233565881-79421429-c7b8-4ccb-84c6-cd35f08b6227.png" width="400">
<img src="https://user-images.githubusercontent.com/101311642/233563824-dbab6976-c527-41ba-b3ba-42bd78a2388e.png" width="400">
