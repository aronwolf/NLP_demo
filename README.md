**Introduction**

This repository is a sample of the work that I have done in natural
language processing for automated keywording and subject extraction and
summarization of electronic textbooks. I have (unfortunately) never had
anyone else to collaborate with on this project, so this code is largely
unreviewed, but I hope it shows the directions in which my brain has
gone when left to my own development devices.

The sample data is significantly reduced so as to not put too much
project-specific content up on the open web, but this codebase is
designed to function optimally with vocabularies of several tens of
thousands of normalized keywords, and roughly as many semantically
significant concept statements.

**Step 0: Setup**
> **Why Python version 2.7?**\
> At the time I was beginning development of this toolset, the support
> for the NLP and ML tools I was interested in implementing was still
> uneven under Python 3, mainly because my own development environment
> involves utilization of images from the Ubuntu Long Term Support
> versions, which, while being more stable than other images, do have a
> tendency to lag behind in terms of currency of software packages
> included. I always planned on upgrading things as I moved forward, and
> the upgrade should not require too much work. And with the upcoming
> release of Ubuntu 20.04LTS, I can move forward with that.
>
> **Basic data structure**
> Why curated metadata?
> Most basically, I decided to use as much of the curated metadata I
> could, as opposed to problematically derived metadata, because it was
> already available, and it was presumably accurate enough to be of use
> to the authoring teams. Since they are the subject matter experts in
> their fields and I am not, I wanted to be able to have access to their
> collective experience. Curated metadata would serve as the skeleton
> upon which would hang the extra weight of the NLP derived
> correspondances.
>
> **What are "Concept Terms"?**
> Concept terms in this context essentially are controlled, mildly
> hierarchical keywords. They are based on the vocabulary available from
> the data dumps from DBPedia.org, with some customization for the
> purposes of the project involved here. They are often taken from the
> technical glossaries of textbooks prepared by the authoring teams,
> used to track the discipline specific concept coverage.
>
> **What are "Learning Statements"?**
> Learning statements are what I have referred to earlier as
> “semantically significant”, since they appear in natural language, and
> can be analyzed for descriptive congruence with the assigned
> individual concept term or terms. Since concept terms are very often
> single words, or at least small 1 to 3 word phrases, there isn’t
> enough semantic structure to programmatically draw any conclusions.
> These constructed learning statements often start as concept term
> definitions, but can include exemplars and factual statements as well.
> The learning statements used in this project are intended to be highly
> formulaic in their grammatical construction, so that they could
> possibly be algorithmically composed at some point.
>
> **EPUB format and glossary.xhtml files**
> EPUB is an industry standard, and an easily parsable complex markup
> format that allowed for great power in xpath and regex based
> extraction of textual elements, such as interstitial learning
> objective statements, which could be used to compare content to the
> semantic statements above. Glossaries that were prepared by the
> authoring teams were used to compare to the existing learning
> statements library to determine concept overlap with existing texts.

**Step 1: Basic Tools**
> **file\_io.py**
> A simple file input/output interface with consistent syntax, and
> several advantages over the basic Pandas xlsx write modules. Also, was
> intended to eventually auto detect file type to allow support for
> multiple formats for upload and export.
> 
> **tokenize\_statements.py**
> A tokenizer and lemmatizer used to preprocess text before the TFIDF
> matrix is constructed. Note the presence of the parts of speech
> identification to allow disambiguation between noun and verb
> homographs.

**Step 2: Importing the data**
> **json\_to\_xlsx.py**
> In order to preserve the UTF8 encoding in the legacy concept
> term/learning statement library, the SQL export was done in json
> format rather than in a csv. This simple module was created to
> reformat the json into an xlsx form that could be uploaded with simple
> file\_io interface.

**Step 3: Ontological Relationships**
> **Why DBPedia?**
> According to DBPedia.org, “DBpedia is a crowd-sourced community effort
> to extract structured content from the information created in various
> Wikimedia projects. This structured information resembles an open
> knowledge graph (OKG) which is available for everyone on the
> Web \[…\] The English version of the DBpedia knowledge base
> describes 4.58 million things, out of which 4.22 million are
> classified in a consistent ontology.” This is a great asset, and will
> always be freely maintained and available. Rather than use on-the-fly
> SPARQL queries to build the ontological map, I elected to download the
> raw RDF semantic triple files. These files were, however, very large,
> some over 7 million lines, and required some special processing in
> order to join them to the terms spreadsheet.
>
> **dbpedia\_redirects.py**
> I elected to use the redirects values in this dataset to represent
> nonpreferred terms. Many of them are simple misspellings, but a great
> many are alternate terms, and the sheer number of terms available make
> this highly useful.
>
> **dbpedia\_skos.py**
> The Simple Knowledge Organization System standard aka SKOS offers
> broader and narrower term relations that are very useful to tie the
> relatively simple knowledge map built by this project together into a
> loose hierarchy, which can then be importing into the graph database
> for representation.

**Step 4: Extract/Transform/Load**
> **Why Neo4j?**
> Neo4j was chosen for the graph database underpinnings because it is an
> open source project, and very powerful in modeling the multiple
> potential data relationships, as well as its scalability. Its easily
> configurable graphical front end in the form of Neo4j Desktop was
> freely available, and very suitable for users who were not familiar or
> comfortable with a command line interface. Since the plan was to
> integrate in a custom developed vocabulary management tool, an open
> source base was necessary.
>
> **etl\_master.py**
> The extract/transform/load function utilizes the derived relationships
> from the DBPedia triple set to construct BT/NT/NPT datasets ready for
> upload into Neo4j using the inbuilt Cypher Query Language. The etl
> master function would also be used as an incremental update while both
> the SQL and the graph databases were being maintained in parallel.
> 
> **etl\_bulk\_transform.py**
> For initial graph db setup, the Cypher queries proved much too slow,
> so the bulk transform module was written to translate the imports into
> a form that could be uploaded expediently via the Neo4j cli admin
> interface.
> 
> **graph\_queries.rtf**
> This is a record of the Cypher queries used for import and
> manipulation of the vocabulary graph.

**Step 5: The NLP Secret Sauce**
> **tf\_idf.py**
>
> The TFIDF vectorizer is the tool that scans the texts and builds up
> term frequency-inverse document frequency term matricies that
> represent the documents to the comparison tools. The TFIDF vectorizer is seperate from the similarity function so that an artificial intelligence algorithm can later be integrated easily to calculate similarity instead of the cosine based calculation below. Experiments are ongoing with TensorFlow and Keras based implementations.
> 
> **similarity.py**
> This simple similarity comparator uses a cosine similarity function to
> calculate the similarities between two documents, specifically in this
> case, concept definitions and learning statements to find concept
> overlap, or text segments and learning statements to infer the
> aboutness of a given piece of text. There is also an experimental
> subroutine in the comments here that artificially boosts the term
> frequency numbers for terms that appear in the curated term list, on
> the assumption that those terms are more indicative of concept
> matching. The effectiveness of this subroutine was a very slight
> increase in accuracy, but the computational overhead made the process
> inefficient, so, while I removed it from my data pipeline, I kept it
> to demonstrate my ongoing experiments with tweaking of results.

**Step 6: Bringing it All Together**
> **vocab\_report.py**
> By using a Cypher query to retrieve only a subset of learning
> statements, based on concept term BT/NT/NPT relationships in the
> graph, this algorithm allows a smaller number of more focused statements to be
> processed, not only faster, but offering more precise results. If the
> Cypher query does not result in any matches for the term, the script
> pulls the entire library as a backup.
