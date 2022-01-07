import hudson.model.*
import jenkins.model.Jenkins
def jobName = 'main-player-matrix-pr'
def q = Jenkins.instance.queue
q.items.findAll { it.task.name.toLowerCase().contains(jobName) }.each { 
 
 println("queued: " + it.task.name)
}
def running = Jenkins.instance.getView('All').getBuilds().findAll{ it.getResult().equals(null) && it.toString().contains(jobName) }
running.each {
 println("running: " + it)
}
