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
            def resFile = "test-result.${NODE_NAME}.txt"
            try {
                sh "python runner.py --pytest \"python -m pytest\" --output \"$resFile\""
            }
            finally {
                archiveArtifacts allowEmptyArchive: true, artifacts: "$resFile"
            }
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

options = new TestAndPublishOptions()
options.skip([StagesEnum.GITHUB_RELEASE])
options.enable([StagesEnum.PACK_RELEASE_DEPS, StagesEnum.PACK_RELEASE_ST_DEPS])
options.setPublishableBranches(['3pc-batch']) //REMOVE IT BEFORE MERGE
options.setPostfixes([master: '3pc-batch']) //REMOVE IT BEFORE MERGE
testAndPublish(name, [ubuntu: testUbuntu], true, options)
