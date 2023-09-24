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

## 🧐 About <a name = "about"></a>


## 🏁 Getting Started <a name = "getting_started"></a>

Export your Apple Watch's health data from the Health app on your iPhone. You can do this by going to the Health app, clicking on your profile picture in the top right corner, and then clicking on "Export All Health Data". This will create a zip file with all of your health data. Unzip this file and place the contents in the `data` directory.

Export your Strong App data by going to the Strong app, clicking on **Profile** \rarrow **Settings** \rarrow **Export Strong Data**. This will create a `.csv` file with all of your Strong data. Place the contents in the `data` directory.


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

Clone the repoisitory
```
git clone {repo}
```

Navigate to the app's directory
```
cd && cd `path_to_app`
```

Run the following in your terminal:
```
docker-compose up -d
```

> :warning: If you need to rebuild and run the container run this command
```
docker-compose up --force-recreate --build -d && docker image prune -f
```