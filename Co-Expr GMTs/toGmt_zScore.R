# newGmt <- list()

# for (n in 1:ncol(listCoAvg[[4]])) {
# 	setOne <- (listCoAvg[[4]])[,n] 
# 	names(setOne) <- rownames(listCoAvg[[4]])

# 	setOne <- sort(setOne)

# 	pop_mean <- mean(setOne)
# 	pop_sd <- sd(setOne)

# 	pop_z <- (setOne - pop_mean) / pop_sd

# 	# cutting off at 3 standard deviations
# 	# cutOff <- sort(pop_z[pop_z >= 3], decreasing = TRUE)
# 	newSet <- names(pop_z[pop_z >= 4]) 

# 	newGmt[[length(newGmt) + 1]] <- newSet
# 	names(newGmt)[length(newGmt)] <- colnames(listCoAvg[[4]])[n]

# }

# by standard deviation cut-off

 newGmt = list()
# # pop_mean = mean(allCrrAvg)
# # pop_sd = sd(allCrrAvg)

for (n in 1:ncol(allCrrAvg)) {
 	setOne = (allCrrAvg)[,n] 
 	names(setOne) = rownames(allCrrAvg)

 	setOne = sort(setOne, decreasing = TRUE)

 	pop_mean = mean(setOne)
 	pop_sd = sd(setOne)

 	pop_z = (setOne - pop_mean) / pop_sd

 	# cutting off at 3 standard deviations
 	# cutOff = sort(pop_z[pop_z >= 3], decreasing = TRUE)
 	newSet = names(pop_z[pop_z >= 3])
 	
 	#creates intersection between newSet and gene_vector
 	#ensures only gene present in original gmt will be in
 	#final gmt
 	newSet = intersect(newSet, gene_vector)

 	newGmt[[length(newGmt) + 1]] = newSet
 	names(newGmt)[length(newGmt)] = colnames(allCrrAvg)[n]

}

for (i in 1:length(newGmt)) {
  cat(names(newGmt)[i], paste0(paste(newGmt[[i]], collapse = "\t"), ""), sep = "\t\t")
  cat("\n")
}

sink("Combined_mouse_coexpr.gmt")



# by size of original GMT

newGmt = list()
# pop_mean = mean(allCorrAvgGrid)
# pop_sd = sd(allCorrAvgGrid)

for (n in 1:ncol(allCrrAvg)) {
	setOne = (allCrrAvg)[,n] 
	names(setOne) = rownames(allCrrAvg)

	setOne = sort(setOne, decreasing = TRUE)

	# pop_mean = mean(setOne)
	# pop_sd = sd(setOne)

	# pop_z = (setOne - pop_mean) / pop_sd

	# cutting off at 3 standard deviations
	# cutOff = sort(pop_z[pop_z >= 3], decreasing = TRUE)
	newSet = setOne[1:length(go[[n]])]

	newGmt[[length(newGmt) + 1]] = names(newSet)
	names(newGmt)[length(newGmt)] = colnames(allCrrAvg)[n]

}