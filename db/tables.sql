CREATE TABLE IF NOT EXISTS node_tree(
       idNode INT NOT NULL,
       level INT NOT NULL,
       iLeft INT,
       iRight INT,
       PRIMARY KEY(idNode)
);

CREATE TABLE IF NOT EXISTS node_tree_names(
       idNode INT NOT NULL FOREIGN KEY(node_tree.idNode),
       language VARCHAR(255) NOT NULL,
       nodeName VARCHAR(255) NOT NULL
);
       
