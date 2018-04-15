class Deployable(object):
    STOP = "Stopped"
    DEPLOYING = 'Deploying'
    DEPLOYED = 'Deployed'
    RETRIEVING = 'Retrieving'
    RETRIEVED = 'Retrieved'
    BROKE = 'Broke'

    def __init__(self, size, deploy_rate, inicial_deployed_size=0):
        self.state = self.STOP
        self.deployed_size = inicial_deployed_size
        self.total_size = size
        self.deploy_rate = deploy_rate

    def update(self, time_elapsed):
        if self.state == self.DEPLOYING:
            self.deployed_size += self.deploy_rate * time_elapsed
            if self.deployed_size >= self.total_size:
                self.deployed_size = self.total_size
                self.state = self.DEPLOYED

        elif self.state == self.RETRIEVING:
            self.deployed_size -= self.deploy_rate * time_elapsed
            if self.deployed_size <= 0:
                self.deployed_size = 0
                self.state = self.RETRIEVED

    def deploy(self):
        if self.state != self.BROKE:
            self.state = self.DEPLOY

    def stop(self):
        if self.state != self.BROKE:
            self.state = self.STOP

    def retrieve(self):
        if self.state != self.BROKE:
            self.state = self.RETRIEVE

    def broke(self):
        self.state = self.BROKE
        self.deployed_size = 0

    def percent_deployed(self):
        return self.deployed_size/self.total_size

    def status(self):
        return "{0} ({1:.0%})".format(self.state, self.deployed_size)

    def __str__(self):
        return self.status()