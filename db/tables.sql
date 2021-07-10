CREATE TABLE IF NOT EXISTS node_tree(
       idNode INT NOT NULL,
       level INT NOT NULL,
       iLeft INT,
       iRight INT,
       PRIMARY KEY(idNode)
);

CREATE TABLE IF NOT EXISTS node_tree_names(
       idNode INT NOT NULL,
       language VARCHAR(255) NOT NULL,
       nodeName VARCHAR(255) NOT NULL,
       FOREIGN KEY(idNode) REFERENCES node_tree(idNode)
);
       
