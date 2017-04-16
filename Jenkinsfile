#!groovy

@Library('SovrinHelpers') _

def name = 'sovrin-client'

def testUbuntu = {
    try {
        echo 'Ubuntu Test: Checkout csm'
        checkout scm

        echo 'Ubuntu Test: Build docker image'
        orientdb.start()

        def testEnv = dockerHelpers.build(name)

        testEnv.inside('--network host') {
            echo 'Ubuntu Test: Install dependencies'

            def sovrinNode = helpers.extractVersion('sovrin-node')
            def sovrinCommon = helpers.extractVersionOfSubdependency(sovrinNode, 'sovrin-common')
            def plenum = helpers.extractVersionOfSubdependency(sovrinCommon, 'plenum')

            deps = [plenum, sovrinNode]
            testHelpers.installDeps(deps)

            echo 'Ubuntu Test: Test'
            sh 'python runner.py --pytest \"python -m pytest\" --output "test-result.txt"'
            //testHelpers.testJunit()
        }
    }
    finally {
        echo 'Ubuntu Test: Cleanup'
        orientdb.stop()
        step([$class: 'WsCleanup'])
    }
}

def testWindows = {
    echo 'TODO: Implement me'
}

def testWindowsNoDocker = {
    try {
        echo 'Windows No Docker Test: Checkout csm'
        checkout scm

        echo 'Windows No Docker Test: drop orientdb databases'
        orientdb.cleanupWindows()


        testHelpers.createVirtualEnvAndExecute({ python, pip ->
            echo 'Windows No Docker Test: Install dependencies'

            def sovrinNode = helpers.extractVersion('sovrin-node')

            testHelpers.installDepsBat(python, pip, [sovrinNode])

            echo 'Windows No Docker Test: Test'
            testHelpers.testJunitBat(python, pip)
        })
    }
    finally {
        echo 'Windows No Docker Test: Cleanup'
        step([$class: 'WsCleanup'])
    }
}

//testAndPublish(name, [ubuntu: testUbuntu, windows: testWindowsNoDocker, windowsNoDocker: testWindowsNoDocker])
testAndPublish(name, [ubuntu: testUbuntu], false) // run tests only

if (env.BRANCH_NAME == '3pc-batch') { // not PR
    def releaseVersion = ''
    stage('Get release version') {
        node('ubuntu-master') {
            releaseVersion = getReleaseVersion()
        }
    }

    testAndPublish.publishPypi('Publish to pypi', [:], releaseVersion)
}
