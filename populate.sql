CREATE TABLE words ( 
	WORD varchar(50) DEFAULT NULL,
	YEAR int DEFAULT NULL,
	OVERALL int DEFAULT NULL,
	DISTINCT_BOOK int DEFAULT NULL
);

\copy words FROM 'jbooks_parsed_mix_removed.txt' WITH delimiter E'\t';