Datasets
========

Clean.Data. needs a comprehensive map of datasets and the connections between them. This GitHub project is focused on solving that problem.

Check out the example_dataset directory for the format of the output datasets. The directory contains 7 output files. Each maps one of the tables in the live website, and is formatted so that it can be directly added to the live website:

#### licenses.json
This is a listing of the available licenses. It's likely that you will need more licenses than are listed here. If so, please create a new file my_licenses.json in your directory, and add extra licenses here. *licenses.json should not be changed*

#### formats.json
This is a listing of the available formats. You will almost certainly need more formats than are listed here. As with licenses, please create a new file my_formats.json in your directory, and add extra formats here. *formats.json should not be changed*

#### organizations.json
This is a listing of the organizations that have responsibility for datasets. The organization should be the actual agency that produces the specific dataset wherever possible. So if the raw data were produced by ConEd, but you're looking at a dataset that's been processed from that data by a research group at NYU, the organization would be the name of the NYU research group.

Names of organizations should be unique - so instead of 'Department of Education', you should use 'Department of Education (DOE), NYC'.

Note that the primary keys here are null. This allows the site to auto-assign a primary key when adding your organizatins to the app.

#### datascientists.json
If a dataset has a specific datascientist responsible for it, add a new datascientist entry here. This requires a first name (must be there, can't be blank), a last name (can be blank, but try not to), and a profile_url (can be blank, but helps with disambiguation). All three of these fields are used when refering to a datascientist from the dataset. 

#### datacatalogs.json
This is a list of catalogs. Each has a name. It can also have a manager and/or a managing organization. These can be null. The name must be unique, and is used as the natural key to reference the catalog. Datasets can have a datacatalog, but do not need to (and most won't).

#### datasets.json
This is the core of the data that will be added in. This maps onto the Dataset model in the data_connections/models.py in the main app.

There are two types of fields. Fields without square brackets are data fields. Fields with square brackets are foreign key relations. The first entry in the datasets.json in the example dataset has comments on each of these fields. They should be explanatory. Post an issue in the issue tracker if you want some clarification.

The foreign key elements all have a means of uniquely identifying a related object. For example: "license": ["MIT"] allows Django to perform a search for the "MIT" license, get it's primary key, and set the foreign key for 'license' approriately for the dataset object. Make sure that you use the correct terms in the foreign key relations. These relations underpin the app.

#### datarelations.json
The connections between datasets are the most important part of the application. In each case, include any information you have about the relationship between the two datasets. This can be as simple as a mirrored dataset, or as complex as a full research paper. The source dataset is the root dataset. The derived dataset is the dataset that was created from it. As before, these are foreign key relations, and need to be carefully specificied.

#### General notes on the format
The files are all standard JSON format files. Many languages have a standard output from their own models to JSON output. Before writing your own JSON output format, check for something like json.dumps(object) in the language you're using.

Note that there's no trailing ',' on the last entry in the list. This will break the data import.

### To Start a Working on a New Directory

* Pick one of the outstanding dataset locations from the Issues list, or add a new Issue for the site you're working on.
* Comment that you're working on it
* Create a new directory and make sure the directory clearly indicates the site.
* Use that directory to store your parsing code as well as your output.
* Make notes on any problems you're having with the site, so that others can help out.
