import rpy2.robjects as ro
from rpy2.robjects.packages import importr
from rpy2.robjects import pandas2ri

pandas2ri.activate()

def optimal_matching(input_sequences_file_dir,output_matrix_file_dir):
    TraMineR = importr('TraMineR')
    ro.r(f"""
        dataset <- read.csv({input_sequences_file_dir})
        sequences_matrix <- as.matrix(dataset[, c("element1", "element2", "element3", "element4", "element5", "element6", "element7")])
        sequences <- seqdef(sequences_matrix)
        om = seqdist(sequences,method="OM",indel=1,sm="TRATE")
        write.csv(om,file={output_matrix_file_dir})
    """)