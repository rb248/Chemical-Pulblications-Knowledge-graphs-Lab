class Queries:
    @staticmethod
    def get_some_publication_wo_img():
        return """
        PREFIX dcterms: <http://purl.org/dc/terms/>
        PREFIX fabio: <http://purl.org/spar/fabio/>
        PREFIX frbr: <http://purl.org/vocab/frbr/core#>
        PREFIX npg: <http://ns.nature.com/terms/>
    
        SELECT DISTINCT ?doi
        WHERE { 
            ?article a fabio:JournalArticle .
            ?article   npg:doi ?doi .
            ?article frbr:embodiment ?manifestations .
            OPTIONAL { ?manifestations frbr:exemplar ?items . }
            BIND(RAND(1 + strlen(str(?doi))*0) as ?rid ) .
        }
        GROUP BY ?doi ?rid
        HAVING (count(?items) = 0)
        ORDER BY ?rid
        LIMIT 1
        """

    # TODO: test for -> will fail
    ## def get_download_link_with_given_doi(doi: str):
    ##    return f"""
    ##    PREFIX fabio: <http://purl.org/spar/fabio/>
    ##    PREFIX npg: <http://ns.nature.com/terms/>
    ##    SELECT count(distinct ?article)
    ##    WHERE {{
    ##        ?article a fabio:JournalArticle .
    ##        ?article npg:doi ?doi .
    ##        ?article frbr:embodiment ?manifestations .
    ##    }}
    ##    HAVING (doi = {doi})
    ## """

    @staticmethod
    def get_download_link_with_given_doi(doi: str):
        return f"""
        PREFIX dcat: <https://www.w3.org/ns/dcat#>
        PREFIX frbr: <http://purl.org/vocab/frbr/core#>
        PREFIX fabio: <http://purl.org/spar/fabio/>
        PREFIX npg: <http://ns.nature.com/terms/>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        SELECT DISTINCT ?doi ?downloadURL ?article
        WHERE {{
            ?article a fabio:JournalArticle ;
                       npg:doi ?doi ;
                       frbr:embodiment ?manifestations .
            FILTER(?doi = "{doi}")
            ?manifestations skos:note ?downloadURL . 
        }}
    """
