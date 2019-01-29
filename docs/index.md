# Invana-bot-extras




**Field transformer** 

The behaviour of the field transformers should be as follow:

- apply field transformers on data and add new field or update the existing field
- tell manager, the path of the field to apply (should mention the traversal of the field and the data types  through wish the path has to be travelled.
- field transformers should be applied one after the other. example: `CleanTitleFieldTf` can be applied first
 and then `NewDocFromSubDocTf` is used to copy the cleaned data into a new collection.



## USECASE 1: traverse the subdocuments and update/create new fields in subdocument.

- [ ] apply transformers and create new field
- [ ] apply transformers and update existing field

```json
/* input data  */
{
    "_id": "5c4ec3bb6f9deb08b186df01",
    "url": "https://www.bing.com/search?q=food%20technology",
    "items": [
        {
            "url": "https://www.sarvgyan.com/courses/engineering/food-technology",
            "title": "Food Technology - Bright Future Ahead for Science Students",
            "description": "Introduction “",
            "item_no": 1
        },
        {
            "url": "https://www.careers360.com/food-technology-course",
            "title": "Food Technology - Careers360",
            "description": "involves a blend of physical, chemical or microbiological processes and techniques for transforming raw ingredients into",
            "item_no": 2
        }

    ],
    "client_info": {
        "client_id": "tcl",
        "topic_id": "technology",
        "keyword": "food technology"
    },
    "updated": "2019-01-28T14:26:27.358Z"
}
```

### Usecase 1.1 : add new field
```json
/* out put data */
{
    "_id": "5c4ec3bb6f9deb08b186df01",
    "url": "https://www.bing.com/search?q=food%20technology",
    "items": [
        {
            "url": "https://www.sarvgyan.com/courses/engineering/food-technology",
            "domain": "www.sarvgyan.com", /* new field created from url field */
            "title": "Food Technology - Bright Future Ahead for Science Students",
            "description": "Introduction “",
            "item_no": 1
        },
        {
            "url": "https://www.careers360.com/food-technology-course",
            "domain": "www.careers360.com",  /* new field created from url field */
            "title": "Food Technology - Careers360",
            "description": "involves a blend of physical, chemical or microbiological processes and techniques for transforming raw ingredients into",
            "item_no": 2
        }

    ],
    "client_info": {
        "client_id": "tcl",
        "topic_id": "technology",
        "keyword": "food technology"
    },
    "updated": "2019-01-28T14:26:27.358Z"
}

```

### Usecase 1.2 : update existing field
```json
/* out put data */
{
    "_id": "5c4ec3bb6f9deb08b186df01",
    "url": "https://www.bing.com/search?q=food%20technology",
    "items": [
        {
            "url": "https://www.sarvgyan.com/courses/engineering/food-technology",
            "title":  "Bright Future Ahead for Science Students", /* title cleaned and updated */
            "description": "Introduction “",
            "item_no": 1
        },
        {
            "url": "https://www.careers360.com/food-technology-course", /* title cleaned and updated */
            "domain": "www.careers360.com",
            "title": "Careers360",
            "description": "involves a blend of physical, chemical or microbiological processes and techniques for transforming raw ingredients into",
            "item_no": 2
        }

    ],
    "client_info": {
        "client_id": "tcl",
        "topic_id": "technology",
        "keyword": "food technology"
    },
    "updated": "2019-01-28T14:26:27.358Z"
}

```
   

## USECASE 2:  save the subdocuments in items field as a new document in a different collection 

ideally elastic search , but lets do mongodb for now just avoid multiple db complexity, 
specify to this transformer, extra fields in the current current main document, 
which need to be copied in to the new entry of subdocument.
 
Ex: NewDocFromSubDocTf(iter_field=“list”, extra_fields=[“client_info”, “updated”]) (syntax may be changed)

extra_fields are from the parent document, and iteration happens onthe `list` field assuming all the fields 
inside are dictionaries.

- [ ] create new document on different collection(or data source)
- [ ] make sure extra fields are also added to the new document.

```json
/* input */
{
    "_id": "5c4ec3bb6f9deb08b186df01",
    "url": "https://www.bing.com/search?q=food%20technology",
    "items": [
        {
            "url": "https://www.sarvgyan.com/courses/engineering/food-technology",
            "title": "Food Technology - Bright Future Ahead for Science Students",
            "description": "Introduction “",
            "item_no": 1
        },
        {
            "url": "https://www.careers360.com/food-technology-course",
            "title": "Food Technology - Careers360",
            "description": "involves a blend of physical, chemical or microbiological processes and techniques for transforming raw ingredients into",
            "item_no": 2
        }

    ],
    "client_info": {
        "client_id": "tcl",
        "topic_id": "technology",
        "keyword": "food technology"
    },
    "updated": "2019-01-28T14:26:27.358Z"
}
```

```json
/* output */
[
    {
        "url": "https://www.sarvgyan.com/courses/engineering/food-technology",
        "title": "Food Technology - Bright Future Ahead for Science Students",
        "description": "Introduction “",
        "item_no": 1,
        "client_info": {
            "client_id": "tcl",
            "topic_id": "technology",
            "keyword": "food technology"
        },
        "updated": "2019-01-28T14:26:27.358Z"
    },
    {
        "url": "https://www.careers360.com/food-technology-course",
        "title": "Food Technology - Careers360",
        "description": "involves a blend of physical, chemical or microbiological processes and techniques for transforming raw ingredients into",
        "item_no": 2,
        "client_info": {
            "client_id": "tcl",
            "topic_id": "technology",
            "keyword": "food technology"
        },
        "updated": "2019-01-28T14:26:27.358Z"
    }

]

```
## Post Job Executor

- [ ] This can be as simple as sending an activity log to the invana crawler server
- [ ] Triggering another pipeline of job [P2 we can discuss]
- [ ] Sending an email notification to the list emails [P2]


## Pre Job Executor

- [ ] This can be as simple as sending an activity log to the invana crawler server







