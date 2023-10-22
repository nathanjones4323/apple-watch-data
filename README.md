<p align="center">
  <a href="" rel="noopener">
 <img width=200px height=200px src="" alt="Project logo"></a>
</p>

<h3 align="center">PyApple Watch</h3>

---

<p align="center"> Parsing your Apple Watch's data exports with Python
    <br> 
</p>

## 📝 Table of Contents

- [About](#about)
- [Getting Started](#getting_started)
- [Usage](#usage)
- [TODO](#todo)

## 🧐 About <a name = "about"></a>


## 🏁 Getting Started <a name = "getting_started"></a>

Export your Apple Watch's health data from the Health app on your iPhone. You can do this by going to the Health app, clicking on your profile picture in the top right corner, and then clicking on "Export All Health Data". 

This will create a zip file with all of your health data. Unzip this file and place the contents in the `data` directory. 

Export your Strong App data by going to the Strong app, clicking on **Profile** ⇨ **Settings** ⇨ **Export Strong Data**.

This will create a `.csv` file with all of your Strong data. Place the contents in the `data` directory.

Clone the repoisitory
```
git clone https://github.com/nathanjones4323/healthy-py.git
```

Navigate to the app's directory
```
cd healthy-py
```

Create a `data` directory in the root of the app
```
mkdir data
```

Add your Apple Watch's health data and Strong App exports to the `data` directory.


Start the container and seed the database with your health data

```
docker-compose -f docker-compose.yml up -d
```

Stop the container

```
docker-compose -f docker-compose.yml down
```

### Prerequisites

Docker ([Docker Desktop comes with Docker](https://www.docker.com/products/docker-desktop/))

## Running the App <a name = "usage"></a>

Navigate to the app's directory
```
cd healthy-py
```

Run the following in your terminal:
```
docker-compose -f docker-compose.yml up -d
```

Stop the container

```
docker-compose -f docker-compose.yml down
```

> :warning: If you need to rebuild and run the container run this command
```
docker-compose up --force-recreate --build -d && docker image prune -f
```

## TODO <a name = "todo"></a>

* `./metabase/docker-entrypoint-initdb.d/create_questions.py` needs to run as a DB init script.
* When initializing Metabase with the automated reports, create the "Strong" `collection` in metabase before the `report_card`
* Data types are broken when you import the `report_card` data into Metabase. Need to fix this.
* Must disable the Friendly display names setting in Metabase admin for the `report_card` data to import correctly. Manual for now
* Find a dynamic way to set the values for 
  * graph.x_axis.title_text
  * graph.y_axis.title_text
  * graph.dimensions
  * graph.metrics