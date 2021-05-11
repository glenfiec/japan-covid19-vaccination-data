suppressWarnings(library(ggplot2))
suppressWarnings(library(scales))
suppressWarnings(library(reshape2))
suppressWarnings(suppressMessages(library(zoo)))

vaccine_data <- read.table("/Volumes/Macintosh HD/Users/cianglenfield/Desktop/japan_vaccine_data/japan_vaccine_data_for_graph.txt", sep = "\t", header = TRUE)
vaccine_data_summary <- read.table("/Volumes/Macintosh HD/Users/cianglenfield/Desktop/japan_vaccine_data/japan_vaccine_data_summaries.txt", sep = "\t", header = FALSE)

total_shots_given <- vaccine_data_summary$V1[1]
overall_population_coverage <- vaccine_data_summary$V2[1]
first_shot_population_coverage <- vaccine_data_summary$V3[1]
second_shot_population_coverage <- vaccine_data_summary$V4[1]

vaccine_data$Date <- factor(vaccine_data$Date, levels = vaccine_data$Date)

reshaped <- reshape2::melt(vaccine_data, id.vars = c("Date", "Total.daily.doses.given", "Basic.doses.given.total"))
reshaped$rolledmean = rollapply(vaccine_data$Total.daily.doses.given, width = 7, FUN = mean, align = "right", partial = TRUE)

vaccine_graph <- ggplot(reshaped, aes(x = Date, y = value, fill = variable)) + 
  geom_col() + 
  theme(axis.text.x = element_text(angle = 45, hjust = 1, vjust = 0.9, size = 7.5), plot.title = element_text(face = "bold", hjust = 0.5)) + 
  scale_y_continuous(name = "Total daily doses given", label = comma, limits = c(0, 800000)) + 
  scale_fill_manual(name = "", labels = c("First dose", "Second dose"), values = c("#F8766D", "#00BA38")) + 
  geom_text(data = reshaped, aes(x = Date, y = Total.daily.doses.given, label = Basic.doses.given.total, angle = 90, hjust = -0.7)) +
  geom_smooth(method = 'loess', formula = y~x, aes(y = reshaped$rolledmean, group = 1, colour = "7 day rolling\n average"), size = 0.7, span = 0.1, se = F) + 
  labs(title = "COVID-19 vaccination progress in Japan", caption = "Data sources: Japan Ministry of Health, Labour and Welfare\n and Prime Minister's Office of Japan\nJapan population: 126,300,000 (World Bank)\nVaccines approved (1): Pfizer/BioNTech\nVaccination data for medical workers are compiled the following Monday") + 
  scale_color_manual(name = "", values = c("black")) + 
  guides(fill = guide_legend(override.aes = list(linetype=0))) +
  annotate("text", x = 2, y = 690000, label = paste("Total doses given: ", total_shots_given, "\nFirst dose coverage: ", first_shot_population_coverage, "%\nSecond dose coverage: ", second_shot_population_coverage, "%", sep = ""), hjust = 0, vjust = 1)
vaccine_graph

ggsave("japan_vaccination_rate_plot.png", plot = vaccine_graph, width = 12, height = 5)
ggsave("japan_vaccination_rate_plot.pdf", plot = vaccine_graph, width = 12, height = 5)

