# Exploratory Data Analysis
This repository contains all code regarding the exploratory data analysis. During the course of the challenge we received multiple versions of the dataset. To get a structured understanding of the available data we defined the following pipeline:
1. Identify features from available columns.
2. Consolidate the most complete data in one column per feature. To give this step more structure we divided it by three categories corresponding to the type of data: *raw, qualitative* and *quantitative*.
3. Create reports to generate insight about and clean up the rows. The cleaned dataset is then exported into the `./data` repository.

## Pipeline organisation
We received a total of 4 datasets during the course of this challenge:
- A first version (`v1`) containing data from immoscout with municipality related data added from external sources. 
- A second version (`v2`) containing the data from `v1` plus data scraped from homegate.
- A third version (`kaggle`) roughly in the same format as `v2` with some minor changes.
- A validation set for `kaggle` in the same format.

We structured the code according to these versions. Furthermore we separated the column based analysis (steps 1 & 2) from the row based operations (step 3):
```
.
└── explorative-data-analysis/
    ├── archive/                    # unused and drafted code
    ├── dataWrangling/              # step 1-2
    │   ├── kaggle/                     # kaggle train and test data
    │   │    ├── exports/                   # rendered notebook
    │   │    └── daw.ipynb                  # step 1 & 2
    │   ├── v1/                         # version 1
    │   │    ├── exports/                   # rendered notebooks
    │   │    ├── 1-daw_columns.ipynb        # step 1 
    │   │    ├── 2-daw_raw.ipynb            # step 2 raw data
    │   │    ├── 3-daw_quantitative.ipynb   # step 2 quantitative data
    │   │    └── 4-daw_qualitative.ipynb    # step 2 qualitative data
    │   └── v2/                         # version 2
    │        ├── exports/                   # rendered notebooks
    │        ├── 1-daw_columns.ipynb        # step 1
    │        ├── 2-daw_raw.ipynb            # step 2 raw data
    │        ├── 3-daw_quantitative.ipynb   # step 2 quantitative data
    │        └── 4-daw_qualitative.ipynb    # step 2 qualitative data
    ├── eda/                        # step 3
    │   ├── exports/                    # rendered notebooks
    │   ├── utils/                      # helper code
    │   ├── eda_kaggle.ipynb            # step 3 kaggle data
    │   ├── eda_v1.ipynb                # step 3 v1 data
    │   └── eda_v2.ipynb                # step 3 v2 data
    ├── .gitignore
    └── README.md

```

## Documentation
The full documentation is available under the [docs Repository](https://github.com/Immobilienrechner-Challenge/docs/tree/main/explorative-data-analysis).
