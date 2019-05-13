library(dplyr)
library(readr)

tabela1 <- read_csv("baza/vozila.csv")

tabela1_znamka <- tabela1$znamka %>% unique()


znamka <- data.frame(id_znamka = c(1:16), znamka = tabela1_znamka)
#write.csv(znamka, file = "baza/znamka.csv", row.names= FALSE)

tabela1_model <- tabela1[,c(2,3)]
tabela1_model <- tabela1_model %>% unique()

model <- left_join(znamka, tabela1_model, by = "znamka")
model$id_model <- c(1:149)
model <- model[c(4, 3, 1)]
#write.csv(model, file = "baza/model.csv", row.names = FALSE)

avtomobil <- left_join(tabela1, model, by = "model")
avtomobil$id <- c(1:608)
avtomobil <- avtomobil[c(11, 9, 4, 5, 6, 7, 8)]
#write.csv(avtomobil, file = "baza/avtomobil.csv", row.names = FALSE)
