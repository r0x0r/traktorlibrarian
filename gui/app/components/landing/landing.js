'use strict';

angular.module('librarian')
    .controller('LandingController', ['$scope', '$route', '$rootScope', '$http',
        function ($scope, $route, $rootScope, $http) {
          $rootScope.isBackButtonVisible = false;
            console.log($rootScope.traktorDir);

          $http({
            method: 'POST',
            url: '/',
            data: {
              action: 'initialize'
            }
          }).success(function (data, status, headers, config) {

            $rootScope.volumes = data.volumes;
          });
    }]);
