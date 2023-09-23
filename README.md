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

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See [deployment](#deployment) for notes on how to deploy the project on a live system.

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