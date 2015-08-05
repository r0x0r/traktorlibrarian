'use strict';

angular.module('librarian')
    .controller('LandingController', ['$scope', '$route', '$rootScope',
        function ($scope, $route, $rootScope) {
          $rootScope.isBackButtonVisible = false;
            console.log($rootScope.traktorDir);
    }]);
