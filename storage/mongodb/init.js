//filtrage par identifiant
db.offres_brutes.createIndex({"id": 1})
//filtrage par date de création
db.offres_brutes.createIndex({"dateCreation" : -1 })

//filtrage par identifiant
db.offres_normalisees.createIndex({ "id": 1 })
//filtrage par source
db.offres_normalisees.createIndex({ "source": 1 })
//Filtrage par ville
db.offres_normalisees.createIndex({ "workplace_city": 1 })
//Filtrage par date de réception de l'offre
db.offres_normalisees.createIndex({ "collected_at": -1 })
